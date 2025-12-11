"""FastAPI backend that exposes Notion data as JSON for the frontend."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from database_client import get_notion_data

app = FastAPI(title="Notion Charts API")

# Allow CORS for local frontend development
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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

    return {"count": len(data), "results": data}
