import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.title("주문 수집")

if st.button("Mock 주문 수집"):
    response = requests.post(f"{API_BASE_URL}/orders/collect", timeout=30)
    st.json(response.json())

st.caption("주문 수집 후 매칭된 주문상품은 발주대기 목록으로 생성됩니다.")
