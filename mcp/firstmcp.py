from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
import os
import asyncio
import stat


def loadAPIKeys():
    load_dotenv(override=True)

def setupSandboxPath(relative_path="mcp/sandbox"):
    """Setup sandbox directory with proper permissions for WSL compatibility"""
    # Try project directory first
    project_sandbox = os.path.abspath(os.path.join(os.getcwd(), relative_path))
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(project_sandbox, mode=0o755, exist_ok=True)
        # Ensure write permissions (WSL sometimes has permission issues)
        os.chmod(project_sandbox, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        return project_sandbox
    except (OSError, PermissionError) as e:
        # Fallback to home directory if project directory fails
        print(f"Warning: Could not use project sandbox at {project_sandbox}: {e}")

async def fetchToolsUsingUvx():
    fetch_params = {"command": "uvx", "args": ["mcp-server-fetch"]}
    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=60) as server:
        fetch_tools = await server.list_tools()
    print(fetch_tools)

async def fetchToolsUsingNpx():
    playwright_params = {"command": "npx","args": [ "@playwright/mcp@latest"]}
    async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as server:
        fetch_tools = await server.list_tools()
    print(fetch_tools)

async def fetchToolsForFileSystem():
    sandbox_path = setupSandboxPath()
    files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}

    async with MCPServerStdio(params=files_params,client_session_timeout_seconds=60) as server:
        file_tools = await server.list_tools()
    print(file_tools)

async def runAgentsWithMCPServers():
    instructions = """
        You browse the internet to accomplish your instructions.
        You are highly capable at browsing the internet independently to accomplish your task, 
        including accepting all cookies and clicking 'not now' as
        appropriate to get to the content you need. If one website isn't fruitful, try another. 
        Be persistent until you have solved your assignment,
        trying different options and sites as needed.
        """
    sandbox_path = setupSandboxPath()
    files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}
    playwright_params = {"command": "npx","args": [ "@playwright/mcp@latest"]}

    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as mcp_server_files:
        async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as mcp_server_browser:
            agent = Agent(
                name="investigator", 
                instructions=instructions, 
                model="gpt-4.1-mini",
                mcp_servers=[mcp_server_files, mcp_server_browser]
                )
            with trace("investigate"):
                result = await Runner.run(agent, "Find a great recipe for Banoffee Pie, then summarize it in markdown to banoffee.md. Please create a file in the sandbox directory. Dont ask just write.")
                print(result.final_output)
if __name__ == "__main__" :
     loadAPIKeys()
    #  asyncio.run(fetchToolsUsingUvx())
     asyncio.run(runAgentsWithMCPServers())