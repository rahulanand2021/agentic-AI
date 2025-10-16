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

class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")

class WebSearchAgentWithPlannerAndStructuredOutputManager:
    def __init__(self):
        self.load_api_keys()
        self.web_search_planner_agents = self.create_web_search_planner_agents()
        self.web_search_agents = self.create_search_agents()
        self.writer_agent = self.create_writer_agent()
        self.email_agent = self.create_email_agent()

    def load_api_keys(self):
        """Load API keys from .env"""
        load_dotenv(override=True)

    def create_search_agents(self):
        INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
        produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
        words. Capture the main points. Write succintly, no need to have complete sentences or good \
        grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
        essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
        
        search_agent = Agent(
            name="Search Agent",
            instructions=INSTRUCTIONS,
            tools=[WebSearchTool(search_context_size="low")],
            model="gpt-4o-mini",
            model_settings=ModelSettings(tool_choice="required"),)    
        return search_agent

    def create_web_search_planner_agents(self): #planner agent

        HOW_MANY_SEARCHES = 3
        INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
        to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

        web_search_planner_agent  = Agent(
        name="PlannerAgent",
        instructions=INSTRUCTIONS,
        model="gpt-4o-mini",
        output_type=WebSearchPlan)

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
    
    def create_email_agent(self):
        INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
        You will be provided with a detailed report. You should use your tool to send one email, providing the 
        report converted into clean, well presented HTML with an appropriate subject line."""

        email_agent = Agent(
            name="Email Agent",
            instructions=INSTRUCTIONS,
            tools=[self.sendHTMLSalesEmail],
            model="gpt-4o-mini"
        )
        return email_agent

    def create_writer_agent(self):  
        INSTRUCTIONS = (
            "You are a senior researcher tasked with writing a cohesive report for a research query. "
            "You will be provided with the original query, and some initial research done by a research assistant.\n"
            "You should first come up with an outline for the report that describes the structure and "
            "flow of the report. Then, generate the report and return that as your final output.\n"
            "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
            "for 5-10 pages of content, at least 1000 words."
            )
        
        writer_agent = Agent(
            name="Writer Agent",
            instructions=INSTRUCTIONS,
            model="gpt-4o-mini",
            output_type=ReportData
        )
        return writer_agent

    async def plan_searches(self, query: str):
        """ Use the planner_agent to plan which searches to run for the query """
        print("Planning searches...")
        result = await Runner.run(self.web_search_planner_agents, f"Query: {query}")
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output

    async def perform_searches(self, search_plan: WebSearchPlan):
        """ Call search() for each item in the search plan """
        print("Searching...")
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = await asyncio.gather(*tasks)
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem):
        """ Use the search agent to run a web search for each item in the search plan """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        result = await Runner.run(self.web_search_agents, input)
        return result.final_output

    async def write_report(self, query: str, search_results: list[str]):
        """ Use the writer agent to write a report based on the search results"""
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(self.writer_agent, input)
        print("Finished writing report")
        return result.final_output

    async def send_email(self, report: ReportData):
        """ Use the email agent to send an email with the report """
        print("Writing email...")
        result = await Runner.run(self.email_agent, report.markdown_report)
        print("Email sent", result.final_output)

    async def main(self):   #structured output agent
        query ="Latest AI Agent frameworks in 2025"

        with trace("Research trace"):
            print("Starting research...")
            search_plan = await self.plan_searches(query)
            search_results = await self.perform_searches(search_plan)
            report = await self.write_report(query, search_results)
            await self.send_email(report)  
            print("Hooray!")

if __name__ == "__main__":
    manager = WebSearchAgentWithPlannerAndStructuredOutputManager()
    asyncio.run(manager.main())