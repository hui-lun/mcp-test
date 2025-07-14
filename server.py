# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources.types import TextResource
from typing import List
from pymongo import MongoClient
import config

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

if __name__ == "__main__":
    mcp.run(transport="stdio")
