# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources.types import TextResource
from typing import List
from pymongo import MongoClient
import config
import requests

# 初始化 FastMCP Agent
mcp = FastMCP("MongoAgent")

@mcp.tool()
def get_people_in_bdm_info(context: TextResource) -> List[str]:
    """
    查詢 BDM-mgmt 資料庫中的 BDM-info collection，有哪些人
    """
    # 預設 collection name，也可根據 context.name 或 uri 擴充
    collection_name = "BDM-info"

    client = MongoClient(config.MONGODB_URI)
    collection = client[config.DATABASE_NAME][collection_name]

    # 回傳非空的 "Chinese Name"
    results = collection.find({}, {"Chinese Name": 1})
    return [doc["Chinese Name"] for doc in results if doc.get("Chinese Name")]

@mcp.tool()
def search(query: str) -> str:
    """
    搜索關鍵字，只回傳 content
    """
    url = (
        f"{config.SEARXNG_API}/search"
        f"?q={query}"
        f"&format=json"
        f"&time_range=month"
        f"&language=zh-TW"
        f"&num=10"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            return "搜尋結果解析失敗"
        contents = [i.get("content", "") for i in data.get("results", []) if i.get("content")]
        if not contents:
            return "查無相關內容"
        return "\n".join(contents)
    except requests.exceptions.RequestException as e:
        return f"搜尋過程發生錯誤: {e}"
if __name__ == "__main__":
    mcp.run(transport="stdio")
