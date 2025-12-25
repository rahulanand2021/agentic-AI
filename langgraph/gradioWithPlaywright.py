from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import gradio as gr
from langgraph.prebuilt import ToolNode, tools_condition
import os
from langchain.agents import Tool
from mailersend import MailerSendClient, EmailBuilder
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
# nest_asyncio - commented out as it may interfere with ProactorEventLoop subprocess support
import textwrap
import asyncio
import sys
import nest_asyncio


# Fix event loop policy for Windows - Playwright requires ProactorEventLoop for subprocess support
# This must be set BEFORE any event loops are created
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Note: nest_asyncio may interfere with ProactorEventLoop's subprocess support
# Try without it first - ProactorEventLoop should work with Gradio
# If Gradio fails, we may need to handle async differently
nest_asyncio.apply()

class State(TypedDict):
    messages: Annotated[list, add_messages]


def loadAPIKeys():
    load_dotenv(override=True)


async def testPlaywright():
    async_browser = create_async_playwright_browser(headless=False)  # headful mode
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
    tools = toolkit.get_tools()
    
    tool_dict = {tool.name:tool for tool in tools}

    navigate_tool = tool_dict.get("navigate_browser")
    extract_text_tool = tool_dict.get("extract_text")

        
    await navigate_tool.arun({"url": "https://www.bbc.com"})
    text = await extract_text_tool.arun({})
    print(textwrap.fill(text))

def emailAndPlaywrightTools():
    global all_tools, async_browser

    # create_async_playwright_browser is a sync function that returns an async browser
    # Use headless=True for server/LangSmith environments to avoid display issues
    # Set headless=False for local debugging if you want to see the browser
    # Try to initialize browser - this creates a wrapper, connection happens lazily
    print("Initializing Playwright browser...")
    try:
        # Use the same pattern as testPlaywright() which works
        async_browser = create_async_playwright_browser(headless=False)
        print("Browser wrapper created successfully")
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
        tools = toolkit.get_tools()
        print(f"Playwright tools initialized: {len(tools)} tools available")
    except Exception as e:
        print(f"Warning: Failed to initialize Playwright browser: {e}")
        import traceback
        traceback.print_exc()
        print("This may happen in environments without display support.")
        print("Continuing without browser tools...")
        tools = []

    tool_send_email = Tool(
        name="sendEmailUsingMailerSend",
        func=sendEmailUsingMailerSend,
        description="Useful for when you need to send an email"
    )

    all_tools = tools + [tool_send_email]
    return all_tools

def sendEmailUsingMailerSend(body: str):
    api_key = os.getenv("MAILERSEND_API_KEY")
    
    if not api_key:
        error_msg = "Error: MAILERSEND_API_KEY environment variable is not set. Please check your .env file."
        print(error_msg)
        return error_msg

    # Initialize the MailerSend client
    client = MailerSendClient(api_key=api_key)

    # Build the email using the EmailBuilder
    email = (EmailBuilder()
        .from_email("MS_rEYZQ3@test-y7zpl98918o45vx6.mlsender.net", "Rahul")  # Must be your verified domain/sender
        .to("rahulanand2005@gmail.com", "Recipient")
        .subject("Test email")
        .text(body)
        .build())

    # Send the email
    response = client.emails.send(email)
    print(response)
    return response

def chatbot(state: State):
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(all_tools)
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def build_langgraph():
    memory_saver = MemorySaver()
    graph_builder = StateGraph(State)

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools=all_tools))
    graph_builder.add_conditional_edges( "chatbot", tools_condition, "tools")
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph = graph_builder.compile(checkpointer=memory_saver)
    
    ## Use Only if you want to build graph images

    # png_bytes = graph.get_graph().draw_mermaid_png()
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # output_path = os.path.join(current_dir, "graph.png")

    # with open(output_path, "wb") as f:
    #     f.write(png_bytes)

    return graph

async def chat(user_input: str, history):
    config = {"configurable": {"thread_id": "10"}}
    result = await graph.ainvoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
    return result["messages"][-1].content

if __name__ == "__main__":
    global graph, async_browser, all_tools
    loadAPIKeys()
    emailAndPlaywrightTools()
    graph = build_langgraph()
    # asyncio.run(testPlaywright())
    gr.ChatInterface(chat, type="messages").launch(inbrowser=True)
    