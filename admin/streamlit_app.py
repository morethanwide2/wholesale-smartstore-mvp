import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.set_page_config(page_title="도매몰 스마트스토어 MVP", layout="wide")
st.title("도매몰 스마트스토어 MVP")
st.caption("도매몰 상품 수집부터 스마트스토어 Mock 등록, 주문 수집, 발주대기까지 확인하는 관리자 화면입니다.")

try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    st.success(f"FastAPI 연결 상태: {response.json().get('status')}")
except requests.RequestException as exc:
    st.error(f"FastAPI 연결 실패: {exc}")

st.info("왼쪽 페이지 메뉴에서 상품 수집, 마스터 생성, 스마트스토어 등록, 주문 수집 흐름을 실행할 수 있습니다.")
