from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os
from Evaluation import Evaluation

# Global variable for system prompt
system_prompt = ""
name = "Rahul Anand"

def loadAPIKeys():
    load_dotenv(override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if openai_api_key:
        print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
    else:
        print("OpenAI API Key not set - please head to the troubleshooting guide in the setup folder")

def readPdfAndSummary():
    reader = PdfReader("foundation/self/Profile.pdf")
    linkedInText = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            linkedInText += text
    
    with open("foundation/self/summary.txt", "r", encoding="utf-8") as f:
        summary = f.read()

    return linkedInText , summary

def createSystemPrompt(summary, linkedInText):
    global system_prompt
    
    

    system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
    particularly questions related to {name}'s career, background, skills and experience. \
    Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
    You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
    Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
    If you don't know the answer, say so."

    system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedInText}\n\n"
    system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

def chat(message, history):
    openai = OpenAI()
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

# Create a function to set the evaluator system prompt
def setevaluatorSystemPrompt(summary, linkedInText):
    evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
    You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
    The Agent is playing the role of {name} and is representing {name} on their website. \
    The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
    The Agent has been provided with context on {name} in the form of their summary and LinkedIn details. Here's the information:"

    evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{summary}\n\n"
    evaluator_system_prompt += f"\n\n## LinkedIn Profile:\n{linkedInText}\n\n"
    evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."
    return evaluator_system_prompt

def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt

    
if __name__ == "__main__" :
     loadAPIKeys()
     linkedInText , summary = readPdfAndSummary()
     createSystemPrompt(summary, linkedInText)
     gr.ChatInterface(chat, type="messages").launch(inbrowser=True)

     