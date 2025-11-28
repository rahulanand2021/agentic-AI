import re
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from IPython.display import Image, display
import gradio as gr
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import random
import os



class State(BaseModel):
    messages : Annotated[list, add_messages]    

def loadAPIKeys():
    load_dotenv(override=True)

def chatbot_node(old_state: State) -> State:
    llm = ChatOpenAI(model="gpt-4o-mini")
        
    response = llm.invoke(old_state.messages)
    new_state = State(messages=[response])
    return new_state

def build_langgraph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("first_node", chatbot_node)
    graph_builder.add_edge(START, "first_node")
    graph_builder.add_edge("first_node", END)
    graph = graph_builder.compile()
    return graph

def chat(user_input: str, history):
    initial_state = State(messages=[{"role": "user", "content": user_input}])
    result = graph.invoke(initial_state)
    print(result)
    return result['messages'][-1].content
    

if __name__ == "__main__":
    loadAPIKeys()
    global graph
    graph = build_langgraph()
    gr.ChatInterface(chat, type="messages").launch()

    # png_bytes = graph.get_graph().draw_mermaid_png()
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # output_path = os.path.join(current_dir, "graph.png")

    # with open(output_path, "wb") as f:
    #     f.write(png_bytes)
