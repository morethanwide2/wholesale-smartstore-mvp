import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")


def get_json(path: str) -> dict:
    response = requests.get(f"{API_BASE_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def post_json(path: str) -> tuple[int, dict]:
    response = requests.post(f"{API_BASE_URL}{path}", timeout=60)
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, {"message": response.text}


st.title("API Upload Queue")
st.caption("Validated channel API work is queued first so calls can be throttled safely.")

summary = get_json("/api-jobs/summary")
st.subheader("Queue Summary")
col_total, col_pending, col_done, col_failed = st.columns(4)
by_status = summary.get("by_status", {})
col_total.metric("Total", summary.get("total", 0))
col_pending.metric("Pending", by_status.get("pending", 0) + by_status.get("retrying", 0))
col_done.metric("Done", by_status.get("done", 0))
col_failed.metric("Failed", by_status.get("failed", 0))

st.subheader("Rate Limits")
rate_limits = get_json("/settings/api-rate-limits").get("items", [])
st.dataframe(rate_limits, use_container_width=True)

st.divider()
st.subheader("Queued Jobs")

run_limit = st.number_input("Run limit", min_value=1, max_value=100, value=10, step=1)
if st.button("Run Pending Jobs"):
    status_code, result = post_json(f"/api-jobs/run-pending?limit={int(run_limit)}")
    if status_code == 200:
        st.success("Queue worker finished.")
    else:
        st.error("Queue worker failed.")
    st.json(result)

col1, col2 = st.columns(2)
with col1:
    service_name = st.selectbox(
        "Channel",
        options=[
            "all",
            "smartstore",
            "gmarket",
            "auction",
            "elevenstreet",
            "toss_shopping",
            "coupang",
            "lotteon",
            "supplier",
        ],
    )
with col2:
    status = st.selectbox("Status", options=["all", "pending", "retrying", "running", "done", "failed", "cancelled"])

params = []
if service_name != "all":
    params.append(f"service_name={service_name}")
if status != "all":
    params.append(f"status={status}")

path = "/api-jobs"
if params:
    path = f"{path}?{'&'.join(params)}"

jobs = get_json(path).get("items", [])
st.dataframe(jobs, use_container_width=True)

st.divider()
st.subheader("Failure / Retry Dashboard")
failures = summary.get("failures", [])
st.dataframe(failures, use_container_width=True)

failure_ids = [item["id"] for item in failures]
if failure_ids:
    selected_job_id = st.selectbox("Failed or retrying job", failure_ids)
    col_retry, col_cancel = st.columns(2)
    with col_retry:
        if st.button("Retry Now", use_container_width=True):
            status_code, result = post_json(f"/api-jobs/{selected_job_id}/retry-now")
            if status_code == 200:
                st.success("Job moved to pending.")
            else:
                st.error("Retry request failed.")
            st.json(result)
    with col_cancel:
        if st.button("Cancel Job", use_container_width=True):
            status_code, result = post_json(f"/api-jobs/{selected_job_id}/cancel")
            if status_code == 200:
                st.success("Job cancelled.")
            else:
                st.error("Cancel request failed.")
            st.json(result)
else:
    st.info("No failed or retrying jobs.")
