# server.py
import asyncio
from typing import List, Dict, Optional
from pymongo import MongoClient
from mcp.server.fastmcp import FastMCP, Context
import config

mcp = FastMCP("MongoAgent")


@mcp.tool()
def get_all_bdm_names_and_ids(context: Context) -> List[Dict[str, str]]:
    """
    查詢所有人的 Chinese Name 和對應的 BDM_id
    """
    try:
        client = MongoClient(config.MONGODB_URI)
        collection = client[config.DATABASE_NAME][config.COLLECTION_NAME]

        results = collection.find({}, {"Chinese Name": 1, "BDM_id": 1})
        return [
            {"Chinese Name": doc.get("Chinese Name", ""), "BDM_id": doc.get("BDM_id", "")}
            for doc in results
            if doc.get("Chinese Name") and doc.get("BDM_id")
        ]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_all_project_titles(context: Context) -> List[str]:
    """
    查詢 BDM-mgmt 資料庫中的 BDM-project collection，列出所有 Title 欄位
    """
    try:
        client = MongoClient(config.MONGODB_URI)
        db = client["BDM-mgmt"]
        collection = db["BDM-project"]

        results = collection.find({}, {"Title": 1})
        return [doc["Title"] for doc in results if doc.get("Title")]
    except Exception as e:
        return [f"查詢失敗：{str(e)}"]


if __name__ == "__main__":
    mcp.run()
