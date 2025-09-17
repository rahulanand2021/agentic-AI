from dotenv import load_dotenv
from agents import Agent, Runner, trace
import asyncio

def loadAPIKeys():
    global openai_api_key, google_api_key
    load_dotenv(override=True)

async def jokester():

    agent = Agent(name="Jokester", instructions="You are a Joke Teller", model="gpt-4o-mini")
    result = await Runner.run(agent, "Tell me a joke about autonomous AI Agents")

    print(result)




if __name__ == "__main__":
    loadAPIKeys()
    asyncio.run(jokester())