from dotenv import load_dotenv
import os

def loadAPIKeys():
    load_dotenv(override=True)

    openai_api_key = os.getenv('OPENAI_API_KEY')

    if openai_api_key:
        print(f"OpenAI API Key exists and begins {openai_api_key[:8]}")
    else:
        print("OpenAI API Key not set - please head to the troubleshooting guide in the setup folder")

if __name__ == "__main__" :
     loadAPIKeys()