from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

import os

def loadAPIKeys():
    load_dotenv(override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')

    if openai_api_key:
        print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
    else:
        print("OpenAI API Key not set - please head to the troubleshooting guide in the setup folder")

def callOpenAIbusinessQuestion():

    openai = OpenAI()

    question = "Pick a business area that might be worth exploring for an Agentic AI opportunity."
    messages: list[ChatCompletionMessageParam] = [
    {"role": "user", "content": question}
]

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    businessQuestion = response.choices[0].message.content
    print(businessQuestion)
    return businessQuestion

def callOpenAIPainPoint(businessQuestion):
    question = businessQuestion + " Please respond with the answer as a text string point wise"
    openai = OpenAI()
    messages: list[ChatCompletionMessageParam] = [{"role": "user", "content": question}]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    painPoint = response.choices[0].message.content
    print(painPoint)
    return painPoint

def callOpenAISolution(businessQuestion, painPoint):
    question = businessQuestion + " and the pain point is " + painPoint + " Please respond with the answer as a text string point wise"
    openai = OpenAI()
    messages: list[ChatCompletionMessageParam] = [{"role": "user", "content": question}]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    solution = response.choices[0].message.content
    print(solution)
    return solution

if __name__ == "__main__" :
     loadAPIKeys()
     businessQuestion = callOpenAIbusinessQuestion()
     print(businessQuestion)    
     painPoint = callOpenAIPainPoint(businessQuestion)        
     print(painPoint)
     solution = callOpenAISolution(businessQuestion, painPoint)
     print(solution)
     print(f"The solution is: {solution}" )





