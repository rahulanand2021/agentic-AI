from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool, WebSearchTool
from agents.model_settings import ModelSettings
from openai.types.responses import ResponseTextDeltaEvent
from openai import AsyncOpenAI
import asyncio
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from typing import Dict
from pydantic import BaseModel


class WebSearchAgentManager:
    def __init__(self):
        self.load_api_keys()
        self.web_search_agents = self.create_web_search_agents()

    def load_api_keys(self):
        """Load API keys from .env"""
        load_dotenv(override=True)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')

    def create_web_search_agents(self):

        INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
        produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
        words. Capture the main points. Write succintly, no need to have complete sentences or good \
        grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
        essence and ignore any fluff. Do not include any additional commentary other than the summary itself."

        web_search_agent = Agent(
            name="Web Search Agent",
            instructions=INSTRUCTIONS,
            tools=[WebSearchTool(search_context_size="low")],
            model="gpt-4o-mini",
            model_settings=ModelSettings(tool_choice="required"),)    

        return web_search_agent

    async def main(self):
        message = "Latest AI Agent frameworks in 2025"

        with trace("Search using Web Search Agent"):
            result = await Runner.run(self.web_search_agents, message)      
            print(result.final_output)

if __name__ == "__main__":
    manager = WebSearchAgentManager()
    asyncio.run(manager.main())