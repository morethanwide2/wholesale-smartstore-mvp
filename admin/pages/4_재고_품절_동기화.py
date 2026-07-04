import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.title("재고/품절 동기화")

if st.button("재고 동기화 실행"):
    response = requests.post(f"{API_BASE_URL}/inventory/sync", timeout=30)
    st.json(response.json())

masters = requests.get(f"{API_BASE_URL}/master-products", timeout=30).json().get("items", [])
st.dataframe(masters, use_container_width=True)
