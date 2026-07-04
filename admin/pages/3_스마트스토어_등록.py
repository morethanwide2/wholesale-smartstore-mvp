import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")


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


st.title("Smartstore Upload")
st.caption("Validate first. Queue or upload only when the product is ready.")

masters = get_json("/master-products").get("items", [])
ready_masters = [item for item in masters if item.get("status") in {"ready", "listed", "draft"}]

if not ready_masters:
    st.info("No master products are ready. Import supplier products and create a master product first.")
    st.stop()

labels = {
    item["id"]: f'{item["id"]} | {item.get("product_name") or item.get("cleaned_name")} | {item.get("sale_price")} KRW'
    for item in ready_masters
}
selected_master_id = st.selectbox(
    "Master product",
    options=list(labels.keys()),
    format_func=lambda item_id: labels[item_id],
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Validate", use_container_width=True):
        status_code, result = post_json(f"/channels/smartstore/products/{selected_master_id}/validate")
        if status_code == 200 and result.get("valid"):
            st.success("Ready to upload.")
        else:
            st.error("Review is required.")
        st.json(result)

with col2:
    if st.button("Preview JSON", use_container_width=True):
        status_code, result = post_json(f"/channels/smartstore/products/{selected_master_id}/build-payload")
        if status_code >= 400:
            st.error("Failed to build payload.")
        st.json(result)

with col3:
    if st.button("Queue Upload", use_container_width=True):
        status_code, result = post_json(f"/channels/smartstore/products/{selected_master_id}/enqueue-upload")
        if status_code == 200:
            st.success("Queued for API upload.")
        else:
            st.error("Not queued because validation failed.")
        st.json(result)

with col4:
    if st.button("Mock Upload", use_container_width=True):
        status_code, result = post_json(f"/channels/smartstore/products/{selected_master_id}/upload")
        if status_code == 200:
            st.success("Mock upload completed.")
        else:
            st.error("Upload stopped.")
        st.json(result)

st.divider()
st.subheader("Channel Product Profiles")
profiles = get_json("/channels/product-profiles?channel_code=smartstore").get("items", [])
st.dataframe(profiles, use_container_width=True)

st.subheader("Upload Failures")
failures = get_json("/channels/smartstore/upload-failures").get("items", [])
st.dataframe(failures, use_container_width=True)
