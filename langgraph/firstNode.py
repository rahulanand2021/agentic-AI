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

nouns = ["Cabbages", "Unicorns", "Toasters", "Penguins", "Bananas", "Zombies", "Rainbows", "Eels", "Pickles", "Muffins"]
adjectives = ["outrageous", "smelly", "pedantic", "existential", "moody", "sparkly", "untrustworthy", "sarcastic", "squishy", "haunted"]


class State(BaseModel):
    messages : Annotated[list, add_messages]    


def loadAPIKeys():
    load_dotenv(override=True)

def shout(text : Annotated[str, "Some Text for the Compiler"]) -> str:
    print(text.upper())
    return "ok"

def our_first_node(old_state: State) -> State:
    human_message = old_state.messages[0].content
    print("Human Message", human_message)

    if human_message == "RahulAnand":
        reply = f"Rahul is the Best"
    else:
        reply = f"{random.choice(nouns)} are {random.choice(adjectives)}"
        
    messages = [{"role": "assistant", "content": reply}]
    new_state = State(messages=messages)
    return new_state

def build_langgraph():
    graph_builder = StateGraph(State)
    graph_builder.add_node("first_node", our_first_node)
    graph_builder.add_edge(START, "first_node")
    graph_builder.add_edge("first_node", END)
    graph = graph_builder.compile()
    return graph

def chat(user_input: str, history):
    message = {"role":"user", "content":user_input}
    messages = [message]
    state = State(messages=messages)
    result = graph.invoke(state)
    print(result)
    print("Actual response : ", result["messages"][-1].content)
    return result["messages"][-1].content

if __name__ == "__main__":
    global graph
    graph = build_langgraph()
    gr.ChatInterface(chat, type="messages").launch()

    # png_bytes = graph.get_graph().draw_mermaid_png()
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # output_path = os.path.join(current_dir, "graph.png")

    # with open(output_path, "wb") as f:
    #     f.write(png_bytes)
