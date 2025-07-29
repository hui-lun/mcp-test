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
    根據指定的 ProjectModel 型號回傳機器資訊：
    - 若為完整型號，則精確比對並回傳單一筆 exact_match。
    - 若為前綴型號，則回傳所有前綴匹配 prefix_matches。
    """
    import json
    import os
    import logging

    logger = logging.getLogger(__name__)
    model = model.strip()
    model_lower = model.lower()

    spec_path = os.path.join(os.path.dirname(__file__), 'spec.json')
    if not os.path.exists(spec_path):
        return {"error": "找不到 spec.json"}

    exact_match = None
    prefix_matches = []

    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            for item in data:
                if not isinstance(item, dict):
                    continue

                # === 精確比對 ===
                if item.get("ProjectModel") == model:
                    exact_match = item
                    break  # 如果你想早停

                system_info = item.get("systemInfo")
                if (
                    isinstance(system_info, list) and system_info and
                    isinstance(system_info[0], dict) and
                    system_info[0].get("ProjectModel") == model
                ):
                    exact_match = item
                    break  # 如果你想早停

            # === 前綴比對 ===（若沒找到精確結果或想補充多筆）
            for item in data:
                if not isinstance(item, dict):
                    continue

                # 比對外層
                pm = item.get("ProjectModel", "")
                if pm.lower().startswith(model_lower):
                    prefix_matches.append(item)
                    continue

                # 比對 systemInfo[*]
                system_info = item.get("systemInfo")
                if isinstance(system_info, list):
                    for sys in system_info:
                        if isinstance(sys, dict):
                            sys_pm = sys.get("ProjectModel", "")
                            if sys_pm.lower().startswith(model_lower):
                                prefix_matches.append(item)
                                break  # 一筆只加一次

        return {
            "exact_match": exact_match,
            "prefix_matches": prefix_matches
        }

    except Exception as e:
        logger.exception("讀取 spec.json 發生錯誤")
        return {"error": f"讀取失敗：{str(e)}"}



if __name__ == "__main__":
    mcp.run()
