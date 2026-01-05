from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
import os
import asyncio
import stat


def loadAPIKeys():
    load_dotenv(override=True)

async def runAgentsWithMCPServers():

    params = {"command": "npx","args": ["-y", "mcp-memory-libsql"],"env": {"LIBSQL_URL": "file:./rahul.db"}}
    
    server = MCPServerStdio(params=params, client_session_timeout_seconds=30)
    
    await server.__aenter__()

    try:
        tools = await server.list_tools()
        print(tools)
    finally:
        await server.__aexit__(None, None, None)
        await asyncio.sleep(0.2)

if __name__ == "__main__" :
     loadAPIKeys()
    #  asyncio.run(fetchToolsUsingUvx())
     asyncio.run(runAgentsWithMCPServers())