import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.title("상품 수집")

if st.button("Mock 도매몰 상품 수집"):
    response = requests.post(f"{API_BASE_URL}/suppliers/1/import-products", timeout=30)
    st.json(response.json())

products = requests.get(f"{API_BASE_URL}/supplier-products", timeout=30).json().get("items", [])
st.dataframe(products, use_container_width=True)
