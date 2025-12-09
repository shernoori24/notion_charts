"""Notion API client module for database operations."""

import pandas as pd
from notion_client import Client
from config import NOTION_TOKEN, DATABASE_ID

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)


def get_notion_data():
    """Fetch data from Notion database and return as DataFrame."""
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