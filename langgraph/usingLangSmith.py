from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from IPython.display import Image, display
import gradio as gr
from langgraph.prebuilt import ToolNode, tools_condition    
import requests
import os
from langchain_openai import ChatOpenAI
from typing import TypedDict
from langsmith import traceable
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool
from sendgrid.helpers.mail import Mail, Email, To, Content
import sendgrid

class State(TypedDict):
    messages: Annotated[list, add_messages]

def loadAPIKeys():
    load_dotenv(override=True)

def testSearch():
    serper = GoogleSerperAPIWrapper()
    result = serper.run("What is the capital of France?")
    print(result)

def searchUsingTools():
    global tools
    serper = GoogleSerperAPIWrapper()

    tool_search =Tool(
        name="search",
        func=serper.run,
        description="Useful for when you need more information from an online search"
    )
    tool_send_email = Tool(
        name="send_email",
        func=sendTestEmail,
        description="Useful for when you need to send an email"
    )

    tools = [tool_search, tool_send_email]
    return tools

def sendTestEmail(body: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    from_email = Email("rahulanand2006@gmail.com")  # Change to your verified sender
    to_email = To("rahulanand2005@gmail.com")  # Change to your recipient
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(response.status_code)

def chatbot(state: State):
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools(tools)
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def build_langgraph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools=tools))
    graph_builder.add_conditional_edges( "chatbot", tools_condition, "tools")

    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    graph = graph_builder.compile()
    
    ## Use Only if you want to build graph images

    # png_bytes = graph.get_graph().draw_mermaid_png()
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # output_path = os.path.join(current_dir, "graph.png")

    # with open(output_path, "wb") as f:
    #     f.write(png_bytes)
    # return graph
def chat(user_input: str, history):
    result = graph.invoke({"messages": [{"role": "user", "content": user_input}]})
    return result["messages"][-1].content

   

if __name__ == "__main__":
    global graph
    loadAPIKeys()
    searchUsingTools()
    graph = build_langgraph()
    gr.ChatInterface(chat, type="messages").launch(inbrowser=True)
    