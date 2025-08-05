import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

competitors = []
answers = []

from terminal_utils import print_markdown, print_success, print_error, show_loading_spinner



def loadAPIKeys():
    # Load API keys from .env file  
    # Override the .env file with the keys in the environment variables
    # This is a good practice to avoid exposing API keys in the code
    # The .env file is a good place to store API keys
    
    load_dotenv(override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    groq_api_key = os.getenv('GROQ_API_KEY')


    # if openai_api_key:
    #     print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
    # else:
    #     print("OpenAI API Key not set - please head to the troubleshooting guide in the setup folder")

    # if anthropic_api_key:
    #     print(f"Anthropic API Key exists and begins {anthropic_api_key[:8]}")
    # else:
    #     print("Anthropic API Key not set - please head to the troubleshooting guide in the setup folder")

    # if google_api_key:
    #     print(f"Google API Key exists and begins {google_api_key[:8]}")
    # else:
    #     print("Google API Key not set - please head to the troubleshooting guide in the setup folder")

    # if deepseek_api_key:
    #     print(f"DeepSeek API Key exists and begins {deepseek_api_key[:8]}")
    # else:
    #     print("DeepSeek API Key not set - please head to the troubleshooting guide in the setup folder")

    # if groq_api_key:
    #     print(f"Groq API Key exists and begins {groq_api_key[:8]}")
    # else:
    #     print("Groq API Key not set - please head to the troubleshooting guide in the setup folder")

def askChallengingQuestionFromOpenAI():
    question = "Please come up with a challenging, nuanced question that I can ask a number of LLMs to evaluate their intelligence. "
    question += "Answer only with the question, no explanation."
    messages = [{"role": "user", "content": question}]

    openai = OpenAI()
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    question = response.choices[0].message.content
    return question

def answerQuestionFromOpenAI(question):
    messages = [{"role": "user", "content": question}]
    openai = OpenAI()
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    answer = response.choices[0].message.content
    return answer

if __name__ == "__main__" :
     loadAPIKeys()
     question = askChallengingQuestionFromOpenAI()
     print_markdown(question, "AI Question")
     answer = answerQuestionFromOpenAI(question)
     print_markdown(answer, "AI Response")

     competitors.append("OpenAI")
     answers.append(answer)

    #  print_markdown(f"Competitor: {competitors[0]}", "Competitor")
    #  print_markdown(f"Answer: {answers[0]}", "Answer")
     
