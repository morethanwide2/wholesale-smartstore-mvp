import os
import json

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
CHANNELS = [
    "smartstore",
    "coupang",
    "gmarket",
    "auction",
    "elevenstreet",
    "toss_shopping",
    "lotteon",
]


def get_json(path: str) -> dict:
    response = requests.get(f"{API_BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def post_json(path: str) -> tuple[int, dict]:
    response = requests.post(f"{API_BASE_URL}{path}", timeout=30)
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, {"message": response.text}


def patch_json(path: str, payload: dict) -> tuple[int, dict]:
    response = requests.patch(f"{API_BASE_URL}{path}", json=payload, timeout=30)
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, {"message": response.text}


st.title("Channel Product Info")
st.caption("Prepare separate listing data for each marketplace before upload.")

masters = get_json("/master-products").get("items", [])
if not masters:
    st.info("No master products yet.")
    st.stop()

channel_code = st.selectbox("Marketplace", CHANNELS)
required_info = get_json(f"/channels/{channel_code}/required-attributes")
st.info(
    f"Required attributes: {', '.join(required_info.get('required_attributes') or []) or 'none'} | "
    f"Name limit: {required_info.get('name_limit')} chars"
)
master_labels = {
    item["id"]: f'{item["id"]} | {item["internal_product_code"]} | {item["name"]} | {item["sale_price"]} KRW'
    for item in masters
}
selected_master_id = st.selectbox(
    "Master product",
    options=list(master_labels.keys()),
    format_func=lambda item_id: master_labels[item_id],
)

if st.button("Prepare Channel Profile"):
    status_code, result = post_json(f"/channels/{channel_code}/products/{selected_master_id}/prepare-profile")
    if status_code == 200:
        st.success("Channel profile is ready.")
    else:
        st.error("Failed to prepare channel profile.")
    st.json(result)

profiles = get_json(f"/channels/product-profiles?channel_code={channel_code}").get("items", [])
st.subheader("Channel Profiles")
st.dataframe(profiles, use_container_width=True)

selected_profile = next(
    (profile for profile in profiles if profile["master_product_id"] == selected_master_id),
    None,
)

if selected_profile is None:
    st.info("Prepare a channel profile for this master product first.")
    st.stop()

st.subheader("Edit Channel Listing Data")
with st.form("channel_profile_form"):
    channel_product_name = st.text_input(
        "Marketplace product name",
        value=selected_profile.get("channel_product_name") or "",
    )
    channel_category_id = st.text_input(
        "Marketplace category ID",
        value=selected_profile.get("channel_category_id") or "",
    )
    channel_sale_price = st.number_input(
        "Marketplace sale price",
        min_value=0,
        value=int(selected_profile.get("channel_sale_price") or 0),
        step=100,
    )
    channel_shipping_fee = st.number_input(
        "Marketplace shipping fee",
        min_value=0,
        value=int(selected_profile.get("channel_shipping_fee") or 0),
        step=100,
    )
    attributes_text = st.text_area(
        "Marketplace attributes JSON",
        value=json.dumps(selected_profile.get("channel_attributes_json") or {}, ensure_ascii=False, indent=2),
        height=150,
    )
    channel_status = st.selectbox(
        "Channel status",
        options=["draft", "ready", "queued", "uploaded", "failed", "paused"],
        index=["draft", "ready", "queued", "uploaded", "failed", "paused"].index(
            selected_profile.get("channel_status") or "draft"
        ),
    )
    use_master_name = st.checkbox("Use master name", value=bool(selected_profile.get("use_master_name")))
    use_master_price = st.checkbox("Use master price", value=bool(selected_profile.get("use_master_price")))
    use_master_images = st.checkbox("Use master images", value=bool(selected_profile.get("use_master_images")))

    if st.form_submit_button("Save Channel Profile"):
        try:
            attributes = json.loads(attributes_text or "{}")
        except json.JSONDecodeError:
            st.error("Marketplace attributes JSON is invalid.")
        else:
            status_code, result = patch_json(
                f"/channels/product-profiles/{selected_profile['id']}",
                {
                    "channel_product_name": channel_product_name,
                    "channel_category_id": channel_category_id,
                    "channel_sale_price": int(channel_sale_price),
                    "channel_shipping_fee": int(channel_shipping_fee),
                    "channel_attributes_json": attributes,
                    "channel_status": channel_status,
                    "use_master_name": use_master_name,
                    "use_master_price": use_master_price,
                    "use_master_images": use_master_images,
                },
            )
            if status_code == 200:
                st.success("Saved.")
            else:
                st.error("Save failed.")
            st.json(result)

st.subheader("Validation Result")
if st.button("Validate Channel Profile"):
    status_code, result = post_json(f"/channels/product-profiles/{selected_profile['id']}/validate")
    if status_code == 200 and result.get("valid"):
        st.success("Ready for this marketplace.")
    else:
        st.error("Review required before upload.")
    st.json(result)

st.json(selected_profile.get("last_validation_json") or {"status": "not_checked"})
