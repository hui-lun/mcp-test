import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    load_dotenv()

    config = {
        "mcpServers": {
            "MongoDB": {
                "command": "npx",
                "args": [
                    "-y", "mongodb-mcp-server",
                    "--connectionString", "mongodb://admin:password@192.168.1.166:27017/admin",
                    "--readOnly"
                ]
            }
        }
    }

    client = MCPClient.from_dict(config)

    llm = ChatOpenAI(
        model="gemma-3-27b-it",
        openai_api_key="EMPTY",
        openai_api_base=os.getenv("VLLM_API_BASE"),
        streaming=True
    )

    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    result = await agent.run("In the BDM-mgmt database and the BDM-project collection, which person has the most projects?")
    print(f"\n✅ 查詢結果：\n{result}")

if __name__ == "__main__":
    asyncio.run(main())
