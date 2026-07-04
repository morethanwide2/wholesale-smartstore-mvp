import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

st.title("API 로그")

logs = requests.get(f"{API_BASE_URL}/logs/api", timeout=30).json().get("items", [])
st.dataframe(logs, use_container_width=True)
