import json
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


def patch_json(path: str, payload: dict) -> tuple[int, dict]:
    response = requests.patch(f"{API_BASE_URL}{path}", json=payload, timeout=30)
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, {"message": response.text}


st.title("Product Master")
st.caption("Review supplier data and prepare your own sellable product data.")

supplier_products = get_json("/supplier-products").get("items", [])
supplier_labels = {
    item["id"]: f'{item["id"]} | {item["supplier_product_id"]} | {item["name"]}'
    for item in supplier_products
}

with st.expander("1. Create master product from supplier product", expanded=True):
    selected_supplier_product_id = None
    if supplier_labels:
        selected_supplier_product_id = st.selectbox(
            "Supplier product",
            options=list(supplier_labels.keys()),
            format_func=lambda item_id: supplier_labels[item_id],
        )

    if selected_supplier_product_id and st.button("Create Master Product"):
        status_code, result = post_json(f"/master-products/from-supplier/{selected_supplier_product_id}")
        if status_code == 200:
            st.success("Master product is ready.")
        else:
            st.error("Failed to create master product.")
        st.json(result)

masters = get_json("/master-products").get("items", [])
st.subheader("Master Product List")
st.dataframe(masters, use_container_width=True)

if not masters:
    st.info("No master products yet.")
    st.stop()

master_labels = {
    item["id"]: f'{item["id"]} | {item["internal_product_code"]} | {item["name"]} | {item["status"]}'
    for item in masters
}
selected_master_id = st.selectbox(
    "Master product to review/edit",
    options=list(master_labels.keys()),
    format_func=lambda item_id: master_labels[item_id],
)

detail = get_json(f"/master-products/{selected_master_id}")
source = detail["supplier_source"]

tab_source, tab_edit, tab_options, tab_images, tab_review = st.tabs(
    ["Supplier Source", "Selling Info", "Options/Stock", "Images/Detail/Cert", "Review"]
)

with tab_source:
    st.subheader("Supplier Source Data")
    st.json(
        {
            "supplier_product_id": source["supplier_product_id"],
            "raw_product_name": source["raw_product_name"],
            "raw_category": source["raw_category"],
            "brand": source["brand"],
            "manufacturer": source["manufacturer"],
            "origin": source["origin"],
        }
    )
    st.text_area("Raw description", value=source.get("raw_description") or "", height=160, disabled=True)
    st.json({"certification_info": source.get("certification_info") or {}})

with tab_edit:
    st.subheader("Selling Product Info")
    with st.form("master_edit_form"):
        cleaned_name = st.text_input("Selling product name", value=detail.get("cleaned_name") or "")
        category_id = st.text_input("Category", value=detail.get("category_id") or "")
        sale_price = st.number_input("Sale price", min_value=0, value=int(detail.get("sale_price") or 0), step=100)
        shipping_fee = st.number_input("Shipping fee", min_value=0, value=int(detail.get("shipping_fee") or 0), step=100)
        needs_review = st.checkbox("Needs review", value=bool(detail.get("needs_review")))
        description = st.text_area("Detail description", value=detail.get("description") or "", height=220)

        if st.form_submit_button("Save Selling Info"):
            status_code, result = patch_json(
                f"/master-products/{selected_master_id}",
                {
                    "cleaned_name": cleaned_name,
                    "display_name": cleaned_name,
                    "category_id": category_id,
                    "sale_price": int(sale_price),
                    "shipping_fee": int(shipping_fee),
                    "needs_review": needs_review,
                    "description": description,
                },
            )
            if status_code == 200:
                st.success("Saved.")
            else:
                st.error("Save failed.")
            st.json(result)

with tab_options:
    st.subheader("Master Options")
    st.dataframe(detail.get("options", []), use_container_width=True)
    st.subheader("Supplier Options")
    st.dataframe(source.get("options", []), use_container_width=True)

with tab_images:
    st.subheader("Images, Detail Page, Certification")
    main_image_url = st.text_input("Main image URL", value=detail.get("main_image_url") or "")
    detail_images_text = st.text_area(
        "Detail image URLs, one per line",
        value="\n".join(detail.get("detail_image_urls") or []),
        height=100,
    )
    certification_text = st.text_area(
        "Certification JSON",
        value=json.dumps(detail.get("certification_info") or {}, ensure_ascii=False, indent=2),
        height=140,
    )

    if main_image_url:
        st.image(main_image_url, caption="Main image", width=240)

    if st.button("Save Images/Certification"):
        try:
            certification_info = json.loads(certification_text or "{}")
        except json.JSONDecodeError:
            st.error("Certification JSON is invalid.")
        else:
            status_code, result = patch_json(
                f"/master-products/{selected_master_id}",
                {
                    "main_image_url": main_image_url,
                    "detail_image_urls": [line.strip() for line in detail_images_text.splitlines() if line.strip()],
                    "certification_info": certification_info,
                },
            )
            if status_code == 200:
                st.success("Saved.")
            else:
                st.error("Save failed.")
            st.json(result)

with tab_review:
    st.subheader("Review Status")
    st.json(
        {
            "status": detail["status"],
            "review_status": detail["review_status"],
            "price_review_required": detail["price_review_required"],
            "needs_review": detail["needs_review"],
            "expected_margin_amount": detail["expected_margin_amount"],
            "margin_rate": detail["margin_rate"],
        }
    )
    if st.button("Approve Review"):
        status_code, result = post_json(f"/master-products/{selected_master_id}/approve")
        if status_code == 200:
            st.success("Approved.")
        else:
            st.error("Approval failed.")
        st.json(result)
