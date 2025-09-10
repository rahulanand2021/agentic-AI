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
    global openai_api_key, google_api_key
    load_dotenv(override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')

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
    if "patent" in message:
        system = system_prompt + "\n\nEverything in your reply needs to be in pig latin - \
              it is mandatory that you respond only and entirely in pig latin"
    else:
        system = system_prompt
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    reply =response.choices[0].message.content

    evaluation = evaluate(reply, message, history)
    
    if evaluation.is_acceptable:
        print("Passed evaluation - returning reply")
    else:
        print("Failed evaluation - retrying")
        print(f"What kind of response was it? : {reply}")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback)       
    return reply

# Create a function to set the evaluator system prompt
def setevaluatorSystemPrompt(summary, linkedInText):
    global evaluator_system_prompt
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

def evaluate(reply, message, history) -> Evaluation:
    gemini = OpenAI(
        api_key=google_api_key, 
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    messages = [{"role": "system", "content": evaluator_system_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    response = gemini.beta.chat.completions.parse(model="gemini-2.0-flash", messages=messages, response_format=Evaluation)
    return response.choices[0].message.parsed

def test_evaluate():
    openai = OpenAI()
    messages = [{"role": "system", "content": system_prompt}] + [{"role": "user", "content": "do you hold a patent?"}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    reply = response.choices[0].message.content
    print(reply)
    evaluation = evaluate(reply, "do you hold a patent?", messages)
    print(evaluation)
    return reply

def rerun(reply, message, history, feedback):
    openai = OpenAI()
    updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

if __name__ == "__main__" :
     loadAPIKeys()
     linkedInText , summary = readPdfAndSummary()
     createSystemPrompt(summary, linkedInText)
     setevaluatorSystemPrompt(summary, linkedInText)
    #  test_evaluate()
     gr.ChatInterface(chat, type="messages").launch(inbrowser=True)

     