"""Main Streamlit application for Notion Charts."""

import streamlit as st
from config import DATABASE_ID
from database_client import get_notion_data
from charts import create_chart

# Page configuration
st.set_page_config(page_title="My Notion Charts", layout="wide")
st.title("Notion Database → Live Charts")
st.markdown("---")

# Get data
try:
    df = get_notion_data()
    if df.empty:
        st.warning("Database is empty or you don't have access!")
        st.stop()
except Exception as e:
    st.error(f"Error connecting to Notion: {e}")
    st.stop()

st.success(f"Number of loaded records: {len(df)}")

# Display raw database (optional)
if st.checkbox("Show raw table"):
    st.dataframe(df, width='stretch')

st.markdown("---")

# Select columns for chart
cols = st.columns(2)
with cols[0]:
    x_column = st.selectbox("X-axis column (e.g., month, category)", options=df.columns)
with cols[1]:
    y_column = st.selectbox("Y-axis column (number)", options=df.columns)

chart_type = st.selectbox("Chart type", [
    "Bar", "Line", "Pie", "Scatter", "Area", "Radar", "Doughnut"
])

# Filter data (optional)
if st.checkbox("Filter data"):
    filter_col = st.selectbox("Filter column", options=df.columns, key="filter_col")
    unique_vals = df[filter_col].dropna().unique()
    selected_vals = st.multiselect("Desired values", options=unique_vals, default=unique_vals)
    df = df[df[filter_col].isin(selected_vals)]

# Build chart
if st.button("Build Chart"):
    fig = create_chart(df, x_column, y_column, chart_type)
    if fig:
        st.plotly_chart(fig, width='stretch')
    else:
        st.error("Y column must be numeric!")

# Manual refresh button
if st.button("Refresh data from Notion"):
    st.cache_data.clear()
    st.rerun()