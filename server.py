# server.py
import asyncio
from typing import List, Dict, Optional
from pymongo import MongoClient
from mcp.server.fastmcp import FastMCP, Context
import config
import json
import os

mcp = FastMCP("MongoAgent")


@mcp.tool()
def get_all_bdm_names_and_ids(context: Context) -> List[Dict[str, str]]:
    """
    Query all users' Chinese Names and corresponding BDM IDs.
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
    Query the BDM-project collection in the BDM-mgmt database and list all Title fields.
    """
    try:
        client = MongoClient(config.MONGODB_URI)
        db = client["BDM-mgmt"]
        collection = db["BDM-project"]

        results = collection.find({}, {"Title": 1})
        return [doc["Title"] for doc in results if doc.get("Title")]
    except Exception as e:
        return [f"查詢失敗：{str(e)}"]


@mcp.tool()
def get_machine_info_by_model(context: Context, model: str) -> dict:
    """
    Return the complete information of the machine based on the specified ProjectModel model.
    """
    import json
    import os
    spec_path = os.path.join(os.path.dirname(__file__), 'spec.json')
    if not os.path.exists(spec_path):
        return {"error": "找不到 spec.json"}
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if not isinstance(item, dict):
                    continue
                # First match the outermost ProjectModel
                if item.get("ProjectModel") == model:
                    return item
                # Then match the ProjectModel in systemInfo[0]
                system_info = item.get("systemInfo")
                if system_info and isinstance(system_info, list) and system_info:
                    if system_info[0].get("ProjectModel") == model:
                        return item
        return {"error": f"找不到型號為 {model} 的機器資訊"}
    except Exception as e:
        return {"error": f"讀取失敗：{str(e)}"}


if __name__ == "__main__":
    mcp.run()
