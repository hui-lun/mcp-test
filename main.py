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
    # Start the MCP Server using stdio transport
    server_params = StdioServerParameters(
        command="python",
        args=["/app/server.py"]  # Change to ["server.py"] if running locally
    )

    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # Initialize the MCP session
            await session.initialize()

            # Load the tools provided by the MCP Server
            tools = await load_mcp_tools(session)
            print("Loaded MCP tools:", [tool.name for tool in tools])

            # Configure the LLM (adjust VLLM_API_BASE to your local deployment)
            llm = ChatOpenAI(
                model="gemma-3-27b-it",
                openai_api_key="EMPTY",
                openai_api_base=os.environ.get("VLLM_API_BASE", "http://192.168.1.120:8090/v1"),
                streaming=True,
                temperature=0.1,
            )

            # Create a ReAct agent with reasoning and tool usage capabilities
            agent = create_react_agent(llm, tools)

            # System + User messages (agent will decide which tool to invoke)
            user_query = input("請輸入查詢內容：")
            messages = [
                SystemMessage(
                    content="你是 BDM 專案資料助手，可以使用 get_machine_info_by_model 工具查詢指定 ProjectModel 型號的詳細資料。" \
                            "請使用工具 get_all_bdm_names_and_ids，列出所有 BDM 的名字和編號。" \
                            "請使用工具 get_all_project_titles，列出所有專案的 Title。"
                ),
                HumanMessage(
                    content=user_query
                )
            ]
            # Run agent reasoning + tool selection + response
            result = await agent.ainvoke({"messages": messages})

            # Print the final AI response
            print("✅ Query result:\n", result.get("messages")[-1].content)

if __name__ == "__main__":
    asyncio.run(main())
