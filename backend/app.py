"""FastAPI backend that exposes Notion data as JSON for the frontend."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from database_client import get_notion_data
import json
import traceback
import pandas as pd
from fastapi.responses import Response

app = FastAPI(title="Notion Charts API")

# Allow CORS for local frontend development
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/data")
async def read_data():
    """Return Notion data as JSON (list of objects)."""

    try:
        df = get_notion_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Convert DataFrame to JSON-serializable list
    try:
        data = df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serialize data: {e}")

    # sanitize NaN -> None for JSON compatibility
    sanitized = []
    for row in data:
        sanitized.append({k: (None if pd.isna(v) else v) for k, v in row.items()})

    return {"count": len(sanitized), "results": sanitized}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/debug")
async def debug_data():
    """Debug endpoint that returns raw JSON (helps inspect serialization issues)."""
    try:
        df = get_notion_data()
        data = df.to_dict(orient="records")
        # Use ensure_ascii=False to preserve UTF-8 characters and return proper bytes
        text = json.dumps({"count": len(data), "results": data}, ensure_ascii=False)
        return Response(content=text, media_type="application/json; charset=utf-8")
    except Exception as e:
        tb = traceback.format_exc()
        # Return the traceback as plain text for easier debugging
        return Response(content=tb, media_type="text/plain; charset=utf-8", status_code=500)
