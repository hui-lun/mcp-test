# main.py
import asyncio
import os
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

async def main():
    # 啟動 MCP Server（使用 stdio 傳輸）
    server_params = StdioServerParameters(
        command="python",
        args=["/app/server.py"]  # 若是本機可改成 ["server.py"]
    )

    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # 初始化 MCP session
            await session.initialize()

            # 載入 MCP Server 提供的工具
            tools = await load_mcp_tools(session)
            print("🛠️ 已載入 MCP 工具：", [tool.name for tool in tools])

            # 設定 LLM（請根據你本地部署的模型設定 VLLM_API_BASE）
            llm = ChatOpenAI(
                model="gemma-3-27b-it",
                openai_api_key="EMPTY",
                openai_api_base=os.environ.get("VLLM_API_BASE", "http://192.168.1.120:8090/v1"),
                streaming=True,
                temperature=0.1,
            )

            # 建立 ReAct Agent，具備推理與工具使用能力
            agent = create_react_agent(llm, tools)

            # 提示：角色設定 + 使用者問題（Agent 自行決定要用哪個工具）
            messages = [
                SystemMessage(
                    content="你是 BDM 專案資料助手，可以使用 get_all_project_titles 工具查詢所有專案的 Title。" \
                        "請使用工具 get_all_bdm_names_and_ids，列出所有 BDM 的名字和編號。"
                ),
                HumanMessage(
                    content="請列出所有專案的 Title"
                )
            ]
            # 執行推理 + 工具選擇 + 回覆
            result = await agent.ainvoke({"messages": messages})

            # 印出最後一則 AI 回應
            print("✅ 查詢結果：\n", result.get("messages")[-1].content)

if __name__ == "__main__":
    asyncio.run(main())
