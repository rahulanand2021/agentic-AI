# from cgi import print_arguments
from dotenv import load_dotenv
from openai import OpenAI
# from  foundation.terminal_utils import print_success, print_error, print_info, print_markdown

import os

def loadAPIKeys():
    load_dotenv(override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if openai_api_key:
        print(f"OpenAI API Key exists and begins {openai_api_key[:8]}") 
    else:
        print("OpenAI API Key not set - please head to the troubleshooting guide in the setup folder")

def callOpenAIQuestion():

    openai = OpenAI()

    question = "Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."
    messages = [{"role": "user", "content": question}]

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages = messages
    )
    question = response.choices[0].message.content
    print(f"## Question Generated\n\n{question}")
    return question

def callOpenAIAnswer(question):
    question = question + " Please respond with the answer as a text string point wise"
    openai = OpenAI()
    messages = [{"role": "user", "content": question}]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    answer = response.choices[0].message.content
    print(f"## Answer Generated\n\n{answer}")
    return answer


if __name__ == "__main__" :
     print("Starting IQ Assessment Program...")
     loadAPIKeys()
     question = callOpenAIQuestion()        
     answer = callOpenAIAnswer(question) 
     print("Assessment completed!")

