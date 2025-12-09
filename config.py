"""Configuration module for Notion Charts app."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Notion API configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

# Validate required environment variables
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN environment variable is required")

if not DATABASE_ID:
    raise ValueError("DATABASE_ID environment variable is required")