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
    server_params = StdioServerParameters(
        command="python",
        args=["/app/server.py"]  # 修改為正確的路徑
    )

    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            llm = ChatOpenAI(
                model="gemma-3-27b-it",
                openai_api_key="EMPTY",
                openai_api_base=os.environ.get("VLLM_API_BASE", "http://192.168.1.120:8090/v1"),
                streaming=True,
                temperature=0.1,
            )

            agent = create_react_agent(llm, tools)

            # 提示：提醒 Agent 工具呼叫要帶 context.uri 等欄位
            messages = [
                SystemMessage(
                    content=(
                        """You are a helpful AI assistant. For every user question, 
                        you MUST use the provided tool to get the answer. 
                        Do NOT answer directly. Always call the tool and return its result."""
                    )
                ),
                HumanMessage(
                    content="台灣 iphone 16 的發售價格"
                )
            ]

            result = await agent.ainvoke({"messages": messages})
            print("✅ 查詢結果：\n", result.get("messages")[-1].content)

if __name__ == "__main__":
    asyncio.run(main())
