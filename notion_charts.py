import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from notion_client import Client
from dotenv import load_dotenv
import os

load_dotenv()

# Settings
notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("DATABASE_ID")

st.set_page_config(page_title="My Notion Charts", layout="wide")
st.title("Notion Database → Live Charts")
st.markdown("---")

@st.cache_data(ttl=60)  # Refresh data every 60 seconds
def get_notion_data():
    # First, retrieve the database to find the data_source_id
    database = notion.databases.retrieve(database_id=DATABASE_ID)
    data_source_id = database["data_sources"][0]["id"]
    
    results = []
    response = notion.data_sources.query(data_source_id=data_source_id)
    
    for row in response["results"]:
        props = row["properties"]
        item = {}
        for key, value in props.items():
            # Support for various Notion property types
            if value["type"] == "title":
                item[key] = value["title"][0]["plain_text"] if value["title"] else ""
            elif value["type"] == "rich_text":
                item[key] = value["rich_text"][0]["plain_text"] if value["rich_text"] else ""
            elif value["type"] == "select":
                item[key] = value["select"]["name"] if value["select"] else None
            elif value["type"] == "multi_select":
                item[key] = ", ".join([opt["name"] for opt in value["multi_select"]])
            elif value["type"] == "number":
                item[key] = value["number"]
            elif value["type"] == "date":
                item[key] = value["date"]["start"] if value["date"] else None
            elif value["type"] == "checkbox":
                item[key] = value["checkbox"]
            else:
                item[key] = str(value[value["type"]])
        results.append(item)
    
    return pd.DataFrame(results)

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
    if df[x_column].dtype == "object" and df[y_column].dtype in ["int64", "float64"]:
        if chart_type == "Bar":
            fig = px.bar(df, x=x_column, y=y_column, color=x_column, title=y_column)
        elif chart_type == "Line":
            fig = px.line(df, x=x_column, y=y_column, markers=True, title=y_column)
        elif chart_type == "Pie":
            fig = px.pie(df, names=x_column, values=y_column, title=y_column)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_column, y=y_column, size=y_column, color=x_column)
        elif chart_type == "Area":
            fig = px.area(df, x=x_column, y=y_column)
        elif chart_type == "Radar":
            fig = go.Figure(data=go.Scatterpolar(r=df[y_column], theta=df[x_column], fill='toself'))
        elif chart_type == "Doughnut":
            fig = go.Figure(data=[go.Pie(labels=df[x_column], values=df[y_column], hole=0.4)])
            fig.update_layout(title=y_column)
        else:
            fig = px.bar(df, x=x_column, y=y_column)

        fig.update_layout(height=600, template="simple_white")
        st.plotly_chart(fig, width='stretch')
    else:
        st.error("Y column must be numeric!")

# Manual refresh button
if st.button("Refresh data from Notion"):
    st.cache_data.clear()
    st.rerun()