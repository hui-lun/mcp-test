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


@mcp.tool()
def get_all_machine_models(context: Context) -> List[str]:
    """
    從 spec.json 讀取所有資料，回傳所有機器型號（ProjectModel）清單。
    若 ProjectModel 不在最外層，則嘗試從 systemInfo[0] 取得。
    """
    import json
    import os
    models = set()
    spec_path = os.path.join(os.path.dirname(__file__), 'spec.json')
    if not os.path.exists(spec_path):
        return ["找不到 spec.json"]
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            data = json.load(f)  # 一次讀取整個 JSON 陣列
            for item in data:
                if not isinstance(item, dict):
                    continue
                model = item.get("ProjectModel")
                if not model:
                    system_info = item.get("systemInfo")
                    if system_info and isinstance(system_info, list) and system_info:
                        model = system_info[0].get("ProjectModel")
                if model:
                    models.add(model)
        return list(models) if models else ["找不到任何機器型號"]
    except Exception as e:
        return [f"讀取失敗：{str(e)}"]


@mcp.tool()
def get_machine_info_by_model(context: Context, model: str) -> dict:
    """
    根據指定的 ProjectModel 型號，回傳該機器的完整資訊。
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
                # 先比對最外層 ProjectModel
                if item.get("ProjectModel") == model:
                    return item
                # 再比對 systemInfo[0] 裡的 ProjectModel
                system_info = item.get("systemInfo")
                if system_info and isinstance(system_info, list) and system_info:
                    if system_info[0].get("ProjectModel") == model:
                        return item
        return {"error": f"找不到型號為 {model} 的機器資訊"}
    except Exception as e:
        return {"error": f"讀取失敗：{str(e)}"}


if __name__ == "__main__":
    mcp.run()
