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
from pydantic import BaseModel, Field

# Define the Schema of our response - this is known as "Structured Outputs"
# With massive thanks to student Wes C. for discovering and fixing a nasty bug with this!

class WebSearchItem(BaseModel):
    """A single web search to perform to best answer the query."""
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    """A plan of web searches to perform to best answer the query."""
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

class WebSearchAgentWithPlannerAndStructuredOutputManager:
    def __init__(self):
        self.load_api_keys()
        self.web_search_planner_agents = self.create_web_search_planner_agents()

    def load_api_keys(self):
        """Load API keys from .env"""
        load_dotenv(override=True)

    def create_web_search_planner_agents(self): #planner agent

        HOW_MANY_SEARCHES = 3
        INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
        to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

        web_search_planner_agent  = Agent(
        name="PlannerAgent",
        instructions=INSTRUCTIONS,
        model="gpt-4o-mini",
        output_type=WebSearchPlan,
        )      

        return web_search_planner_agent
    @function_tool(description_override="This Tool Sends Cold Sales Email")
    @staticmethod
    def sendHTMLSalesEmail(subject: str, html_body: str) -> Dict[str, str]:
        sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        from_email = Email("rahulanand2006@gmail.com")  # Change to your verified sender
        to_email = To("rahulanand2005@gmail.com")  # Change to your recipient
        content = Content("text/plain", html_body)
        mail = Mail(from_email, to_email, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        return {"status_code": response.status_code}
        
    async def main(self):   #structured output agent
        message = "Latest AI Agent frameworks in 2025"

        with trace("Search using Web Search Agent"):
            result = await Runner.run(self.web_search_planner_agents, message)      
            print(result.final_output)

if __name__ == "__main__":
    manager = WebSearchAgentWithPlannerAndStructuredOutputManager()
    asyncio.run(manager.main())