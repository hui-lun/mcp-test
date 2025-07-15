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
    搜索关键字
    """
    # API URL
    url = f"{config.SEARXNG_API}/search?q=%s&format=json"%query
    try:
        # 发送GET请求
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 将响应内容解析为JSON
            data = response.json()
            result_list=[]
            for i in data["results"]:
                result_list.append(i["content"])
            content="\n".join(result_list)
            return content
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"请求过程中发生错误: {e}")
        return False
if __name__ == "__main__":
    mcp.run(transport="stdio")
