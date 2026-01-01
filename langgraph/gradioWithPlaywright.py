import asyncio
import os
import sys
from typing import Annotated
from typing_extensions import TypedDict

import nest_asyncio
nest_asyncio.apply()

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from dotenv import load_dotenv
import gradio as gr

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langchain_openai import ChatOpenAI
from langchain.agents import Tool

# Use ASYNC browser - this is the correct one for modern LangGraph
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit

from mailersend import MailerSendClient, EmailBuilder

class State(TypedDict):
    messages: Annotated[list, add_messages]

def loadAPIKeys():
    load_dotenv(override=True)

def initialize_playwright_tools():
    """Initialize Playwright tools with async browser"""
    print("Initializing Playwright async browser...")
    try:
        async_browser = create_async_playwright_browser(headless=True)
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
        tools = toolkit.get_tools()
        print(f"Playwright tools initialized: {len(tools)} tools available")
        return tools
    except Exception as e:
        print(f"Failed to initialize Playwright: {e}")
        import traceback
        traceback.print_exc()
        return []

def sendEmailUsingMailerSend(body: str):
    api_key = os.getenv("MAILERSEND_API_KEY")
    if not api_key:
        return "Error: MAILERSEND_API_KEY not set"

    client = MailerSendClient(api_key=api_key)
    email = (EmailBuilder()
             .from_email("MS_rEYZQ3@test-y7zpl98918o45vx6.mlsender.net", "Rahul")
             .to("rahulanand2005@gmail.com", "Recipient")
             .subject("Test email")
             .text(body)
             .build())

    response = client.emails.send(email)
    print("Email sent:", response)
    return str(response)

async def chatbot(state: State):
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(all_tools)
    response = await llm_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}

def build_langgraph():
    memory = MemorySaver()
    builder = StateGraph(State)

    builder.add_node("chatbot", chatbot)
    builder.add_node("tools", ToolNode(tools=all_tools))

    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    builder.add_edge(START, "chatbot")

    return builder.compile(checkpointer=memory)

async def chat_async(user_input: str, history):
    config = {"configurable": {"thread_id": "default_thread"}}
    
    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config
    )
    return result["messages"][-1].content

if __name__ == "__main__":
    global graph, all_tools

    loadAPIKeys()

    playwright_tools = initialize_playwright_tools()

    email_tool = Tool(
        name="sendEmailUsingMailerSend",
        func=sendEmailUsingMailerSend,
        description="Sends an email with the given body text."
    )

    all_tools = playwright_tools + [email_tool]

    graph = build_langgraph()

    print("LangGraph ready. Starting Gradio...")

    gr.ChatInterface(
        fn=chat_async,
        type="messages",
        title="Browser Agent with Playwright",
        description="I can browse the web, navigate pages, extract info, and send emails."
    ).launch(inbrowser=True)