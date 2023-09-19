import streamlit as st
import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()

query = st.text_input(
    "Enter your SQL query", "SELECT * FROM your_project_id.dataset_id.table_id LIMIT 10"
)

results = None


def run_bigquery_query(query):
    query_job = client.query(query)
    return query_job.result().to_dataframe()


if st.button("Run Query"):
    try:
        results = run_bigquery_query(query)
    except Exception as e:
        st.error(f"Error: {e}")

if results is not None:
    st.write(results)
