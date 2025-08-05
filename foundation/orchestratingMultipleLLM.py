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
    
    global openai_api_key, anthropic_api_key, google_api_key, deepseek_api_key, groq_api_key
    
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

def answerQuestionFromAnthropic(question):
    messages = [{"role": "user", "content": question}]
    anthropic = Anthropic()
    response = anthropic.messages.create(
        model="claude-3-7-sonnet-latest",
        messages=messages,
        max_tokens=2000
    )
    answer = response.content[0].text
    return answer

def answerQuestionFromGoogleGemini(question):
    messages = [{"role": "user", "content": question}]
    
    openai = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    model_name = "gemini-2.0-flash"
    response = openai.chat.completions.create(
        model=model_name,
        messages=messages
    )
    answer = response.choices[0].message.content
    return answer

def answerQuestionFromDeepSeek(question):
    messages = [{"role": "user", "content": question}]
    
    openai = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com/v1")
    model_name = "deepseek-chat"
    response = openai.chat.completions.create(
        model=model_name,
        messages=messages
    )
    answer = response.choices[0].message.content
    return answer

def answerQuestionFromGroq(question):
    messages = [{"role": "user", "content": question}]
    
    openai = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
    model_name = "llama-3.3-70b-versatile"
    response = openai.chat.completions.create(
        model=model_name,
        messages=messages
    )
    answer = response.choices[0].message.content
    return answer

def addToLLMList(competitor, answer):
    competitors.append(competitor)
    answers.append(answer)

def getAlltheAnswersTogether():
    together = ""
    for index, answer in enumerate(answers):
        together += f"# Response from competitor {index+1}\n\n"
        together += answer + "\n\n"
    return together

def evaluatingAnswers(question, allAnswers):
    judge = f"""You are judging a competition between {len(competitors)} competitors.
    Each model has been given this question:

    {question}

    Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
    Respond with JSON, and only JSON, with the following format:
    {{"results": ["best competitor number", "second best competitor number", "third best competitor number", ...]}}

    Here are the responses from each competitor:

    {allAnswers}

    Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""

    judge_messages = [{"role": "user", "content": judge}]
    openai = OpenAI()
    response = openai.chat.completions.create(
        model="o3-mini",
        messages=judge_messages
    )
    answer = response.choices[0].message.content
    return answer

def findCompetitorsRanking(results):

    results_dict = json.loads(results)
    ranks = results_dict["results"]
    
    for index, result in enumerate(ranks):
        competitor = competitors[int(result)-1]
        print(f"Rank {index+1}: {competitor}")

if __name__ == "__main__" :
    loadAPIKeys()
    question = askChallengingQuestionFromOpenAI()
    print_markdown(question, "AI Question")

    print("Getting Answer from OpenAI")
    answerOpenAI = answerQuestionFromOpenAI(question)
    addToLLMList("OpenAI", answerOpenAI)
    #  print_markdown(answerOpenAI, "OpenAI Response")

    print("Getting Answer from Anthropic")
    answerAnthropic = answerQuestionFromAnthropic(question)
    addToLLMList("Anthropic", answerAnthropic)
    # print_markdown(answerAnthropic, "Anthropic AI Response")

    print("Getting Answer from Gemini")
    answerGoogleGemini = answerQuestionFromGoogleGemini(question)
    addToLLMList("Google", answerGoogleGemini)
    # print_markdown(answerGoogleGemini, "Google Gemini AI Response")

    print("Getting Answer from DeepSeek")
    answerDeepSeek = answerQuestionFromDeepSeek(question)
    addToLLMList("DeepSeek", answerDeepSeek)
    # print_markdown(answerDeepSeek, "Deep Seek AI Response")

    print("Getting Answer from Groq")
    answerGroq = answerQuestionFromGroq(question)
    addToLLMList("Groq", answerGroq)
    # print_markdown(answerGroq, "Groq AI Response")

    allAnswers = getAlltheAnswersTogether()
    
    print("Evaluating Answers. This might take a while")
    results = evaluatingAnswers(question, allAnswers)

    print(f"Ranking from LLM after evaluation: {results}")
    findCompetitorsRanking(results)

    
     
