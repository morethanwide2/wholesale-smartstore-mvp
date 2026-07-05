import json
import os

import pandas as pd
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


def parse_json(text: str, label: str) -> dict | None:
    try:
        return json.loads(text or "{}")
    except json.JSONDecodeError as exc:
        st.error(f"{label} JSON 형식이 올바르지 않습니다: {exc}")
        return None


st.title("상품 마스터")
st.caption("도매몰 원본을 내 판매상품으로 검수하고, 채널 등록 전에 필요한 값을 보완합니다.")

supplier_products = get_json("/supplier-products").get("items", [])
supplier_labels = {
    item["id"]: f'{item["id"]} | {item["supplier_product_id"]} | {item["name"]}'
    for item in supplier_products
}

with st.expander("1. 수집 상품에서 판매상품 마스터 생성", expanded=True):
    if supplier_labels:
        selected_supplier_product_id = st.selectbox(
            "수집 상품",
            options=list(supplier_labels.keys()),
            format_func=lambda item_id: supplier_labels[item_id],
        )
        if st.button("판매상품 마스터 생성"):
            status_code, result = post_json(f"/master-products/from-supplier/{selected_supplier_product_id}")
            st.success("생성 또는 기존 마스터 확인 완료") if status_code == 200 else st.error("마스터 생성 실패")
            st.json(result)
    else:
        st.info("먼저 상품 수집을 실행하세요.")

masters = get_json("/master-products").get("items", [])
st.subheader("마스터 상품 목록")
st.dataframe(masters, use_container_width=True)

if not masters:
    st.stop()

master_labels = {
    item["id"]: f'{item["id"]} | {item["internal_product_code"]} | {item["name"]} | {item["status"]} | 검증:{item.get("validation_status", "not_checked")}'
    for item in masters
}
selected_master_id = st.selectbox(
    "검수/수정할 마스터 상품",
    options=list(master_labels.keys()),
    format_func=lambda item_id: master_labels[item_id],
)

detail = get_json(f"/master-products/{selected_master_id}")
source = detail["supplier_source"]

tab_source, tab_selling, tab_options, tab_media, tab_validate = st.tabs(
    ["도매몰 원본", "판매정보", "옵션/재고", "이미지/상세/인증", "등록 전 검증"]
)

with tab_source:
    st.subheader("도매몰에서 가져온 원본 정보")
    col1, col2 = st.columns(2)
    with col1:
        st.write("상품명")
        st.code(source.get("raw_product_name") or "")
        st.write("카테고리")
        st.code(source.get("raw_category") or "")
        st.write("브랜드 / 제조사 / 원산지")
        st.json({"brand": source.get("brand"), "manufacturer": source.get("manufacturer"), "origin": source.get("origin")})
    with col2:
        if source.get("main_image_url"):
            st.image(source["main_image_url"], caption="도매몰 대표이미지", width=240)
        st.write("인증정보")
        st.json(source.get("certification_info") or {})
    st.text_area("도매몰 상세설명", value=source.get("raw_description") or "", height=180, disabled=True)
    st.write("도매몰 옵션")
    st.dataframe(source.get("options", []), use_container_width=True)

with tab_selling:
    st.subheader("내가 판매할 상품 정보")
    with st.form("master_selling_form"):
        cleaned_name = st.text_input("판매 상품명", value=detail.get("cleaned_name") or "")
        category_id = st.text_input("채널 공통 카테고리/매핑 코드", value=detail.get("category_id") or "")
        col1, col2, col3 = st.columns(3)
        with col1:
            brand = st.text_input("브랜드", value=detail.get("brand") or "")
        with col2:
            manufacturer = st.text_input("제조사", value=detail.get("manufacturer") or "")
        with col3:
            origin = st.text_input("원산지", value=detail.get("origin") or "")
        col4, col5 = st.columns(2)
        with col4:
            sale_price = st.number_input("판매가", min_value=0, value=int(detail.get("sale_price") or 0), step=100)
        with col5:
            shipping_fee = st.number_input("배송비", min_value=0, value=int(detail.get("shipping_fee") or 0), step=100)
        search_tags_text = st.text_input("검색 태그", value=", ".join(detail.get("search_tags") or []))
        needs_review = st.checkbox("관리자 검수 필요", value=bool(detail.get("needs_review")))
        description = st.text_area("상세설명 HTML/문구", value=detail.get("description") or "", height=240)

        if st.form_submit_button("판매정보 저장"):
            tags = [tag.strip() for tag in search_tags_text.split(",") if tag.strip()]
            status_code, result = patch_json(
                f"/master-products/{selected_master_id}",
                {
                    "cleaned_name": cleaned_name,
                    "display_name": cleaned_name,
                    "category_id": category_id,
                    "brand": brand,
                    "manufacturer": manufacturer,
                    "origin": origin,
                    "sale_price": int(sale_price),
                    "shipping_fee": int(shipping_fee),
                    "search_tags": tags,
                    "needs_review": needs_review,
                    "description": description,
                },
            )
            st.success("저장 완료") if status_code == 200 else st.error("저장 실패")
            st.json(result)

with tab_options:
    st.subheader("내 판매 옵션")
    options = detail.get("options", [])
    st.dataframe(options, use_container_width=True)
    if options:
        option_labels = {
            option["id"]: f'{option["internal_option_code"]} | {option.get("option_name") or ""} {option.get("option_value") or ""} | {option["status"]}'
            for option in options
        }
        option_id = st.selectbox("수정할 옵션", options=list(option_labels.keys()), format_func=lambda item_id: option_labels[item_id])
        selected_option = next(option for option in options if option["id"] == option_id)
        with st.form("option_edit_form"):
            option_name = st.text_input("옵션명", value=selected_option.get("option_name") or "")
            option_value = st.text_input("옵션값", value=selected_option.get("option_value") or "")
            col1, col2, col3 = st.columns(3)
            with col1:
                option_sale_price = st.number_input("옵션 판매가", min_value=0, value=int(selected_option.get("sale_price") or 0), step=100)
            with col2:
                stock_quantity = st.number_input("재고", min_value=0, value=int(selected_option.get("stock_quantity") or 0), step=1)
            with col3:
                statuses = ["active", "sold_out", "discontinued", "needs_review"]
                option_status = st.selectbox("상태", options=statuses, index=statuses.index(selected_option.get("status") or "active"))
            if st.form_submit_button("옵션 저장"):
                status_code, result = patch_json(
                    f"/master-product-options/{option_id}",
                    {
                        "option_name": option_name,
                        "option_value": option_value,
                        "sale_price": int(option_sale_price),
                        "stock_quantity": int(stock_quantity),
                        "status": option_status,
                    },
                )
                st.success("옵션 저장 완료") if status_code == 200 else st.error("옵션 저장 실패")
                st.json(result)

with tab_media:
    st.subheader("대표이미지, 상세이미지, 인증/고시정보")
    main_image_url = st.text_input("대표이미지 URL", value=detail.get("main_image_url") or "")
    detail_images_text = st.text_area("상세이미지 URL, 한 줄에 하나씩", value="\n".join(detail.get("detail_image_urls") or []), height=100)
    certification_text = st.text_area("인증정보 JSON", value=json.dumps(detail.get("certification_info") or {}, ensure_ascii=False, indent=2), height=140)
    notice_text = st.text_area(
        "상품정보고시/채널 필수속성 JSON",
        value=json.dumps(detail.get("notice_info_json") or {}, ensure_ascii=False, indent=2),
        height=160,
        help='예: {"notice_category": "기타", "model_name": "모델명", "material": "소재"}',
    )
    if main_image_url:
        st.image(main_image_url, caption="현재 대표이미지", width=260)
    if st.button("이미지/인증/고시정보 저장"):
        certification_info = parse_json(certification_text, "인증정보")
        notice_info = parse_json(notice_text, "상품정보고시")
        if certification_info is not None and notice_info is not None:
            status_code, result = patch_json(
                f"/master-products/{selected_master_id}",
                {
                    "main_image_url": main_image_url,
                    "detail_image_urls": [line.strip() for line in detail_images_text.splitlines() if line.strip()],
                    "certification_info": certification_info,
                    "notice_info_json": notice_info,
                },
            )
            st.success("저장 완료") if status_code == 200 else st.error("저장 실패")
            st.json(result)

with tab_validate:
    st.subheader("등록 전 검증")
    current_status = {
        "상품상태": detail["status"],
        "검수상태": detail["review_status"],
        "검증상태": detail.get("validation_status"),
        "검수필요": detail["needs_review"],
        "가격검수필요": detail["price_review_required"],
        "예상마진": detail["expected_margin_amount"],
        "마진율": detail["margin_rate"],
    }
    st.json(current_status)
    if detail.get("validation_issues_json"):
        st.write("마지막 검증 이슈")
        st.dataframe(pd.DataFrame(detail["validation_issues_json"]), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("스마트스토어 검증 실행"):
            status_code, result = post_json(f"/channels/smartstore/products/{selected_master_id}/validate")
            if status_code == 200 and result.get("valid"):
                st.success("등록 가능한 상태입니다.")
            elif status_code == 200:
                st.warning("수정 또는 확인이 필요한 항목이 있습니다.")
            else:
                st.error("검증 실패")
            st.json(result)
    with col2:
        if st.button("검수 승인"):
            status_code, result = post_json(f"/master-products/{selected_master_id}/approve")
            st.success("검수 승인 완료") if status_code == 200 else st.error("검수 승인 실패")
            st.json(result)
