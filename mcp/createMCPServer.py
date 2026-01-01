from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from accounts import Account
import asyncio
import os

def loadAPIKeys():
    load_dotenv(override=True)

async def createAccountMCPServer():

    mcp_dir = os.path.dirname(os.path.abspath(__file__))
    accounts_server_path = os.path.join(mcp_dir, "accounts_server.py")
    # Use absolute path - accounts_server.py now handles its own imports
    params = {
        "command": "uv", 
        "args": ["run", accounts_server_path]
    }
    async with MCPServerStdio(params=params, client_session_timeout_seconds=60) as server:
        mcp_tools = await server.list_tools()
    # print(mcp_tools)

async def createMCPClientAgent():
    mcp_dir = os.path.dirname(os.path.abspath(__file__))
    accounts_server_path = os.path.join(mcp_dir, "accounts_server.py")
    # Use absolute path - accounts_server.py now handles its own imports
    params = {
        "command": "uv", 
        "args": ["run", accounts_server_path]
    }

    instructions = "You are able to manage an account for a client, and answer questions about the account."
    request = "My name is Rahul and my account is under the name Rahul. What's my balance and my holdings?"
    model = "gpt-4.1-mini"
    async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as mcp_server:
        agent = Agent(name="account_manager", instructions=instructions, model=model, mcp_servers=[mcp_server])
        with trace("account_manager"):
            result = await Runner.run(agent, request)
    print(result.final_output)

async def main():
    await createAccountMCPServer()
    await createMCPClientAgent()


if __name__ == "__main__" :
     loadAPIKeys()
    #  account = Account.get("Rahul")
    #  print(account)
    #  account.buy_shares("GOOGLE", 3, "Because this bookstore website looks promising")
    #  print(account.report())
     asyncio.run(main())