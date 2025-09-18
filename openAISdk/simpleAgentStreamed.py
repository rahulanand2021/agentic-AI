from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio



def loadAPIKeys():
    global openai_api_key, google_api_key
    load_dotenv(override=True)

def createAgent():
    instructions1 = "You are a sales agent working for ComplAI, \
        a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
        You write professional, serious cold emails."
    
    sales_agent1 = Agent(
                name="Professional Sales Agent",
                instructions=instructions1,
                model="gpt-4o-mini"
                )
    return sales_agent1

async def runAgent(sales_agent):
    result = Runner.run_streamed(sales_agent, input="Write a cold sales email")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

if __name__ == "__main__":
    loadAPIKeys()
    sales_agent1 = createAgent()
    asyncio.run(runAgent(sales_agent1))
