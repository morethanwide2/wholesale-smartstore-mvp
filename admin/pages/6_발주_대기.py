import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.title("발주 대기")

purchase_orders = requests.get(f"{API_BASE_URL}/purchase-orders", timeout=30).json().get("items", [])
st.dataframe(purchase_orders, use_container_width=True)
