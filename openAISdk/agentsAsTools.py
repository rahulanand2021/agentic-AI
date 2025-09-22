from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os


class SalesAgentManager:
    def __init__(self):
        self.load_api_keys()
        self.sales_agents = self.create_sales_agents()

    def load_api_keys(self):
        """Load API keys from .env"""
        load_dotenv(override=True)

    def create_sales_agents(self):
        """Initialize three different styles of sales agents"""
        instructions = {
            "Professional Sales Agent": (
                "You are a sales agent working for ComplAI, "
                "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
                "You write professional, serious cold emails."
            ),
            "Engaging Sales Agent": (
                "You are a humorous, engaging sales agent working for ComplAI, "
                "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
                "You write witty, engaging cold emails that are likely to get a response."
            ),
            "Busy Sales Agent": (
                "You are a busy sales agent working for ComplAI, "
                "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
                "You write concise, to the point cold emails."
            ),
        }

        sales_agent1 = Agent(
                name="Professional Sales Agent",
                instructions=instructions["Busy Sales Agent"],
                model="gpt-4o-mini"
                )

        sales_agent2 = Agent(
                name="Engaging Sales Agent",
                instructions=instructions["Engaging Sales Agent"],
                model="gpt-4o-mini"
                )

        sales_agent3 = Agent(
                name="Busy Sales Agent",
                instructions=instructions["Professional Sales Agent"],
                model="gpt-4o-mini"
                )

        return sales_agent1, sales_agent2, sales_agent3

    @function_tool(description_override="This Tool Sends Cold Sales Email")
    @staticmethod
    def sendSalesEmail(body: str):
        sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        from_email = Email("rahulanand2006@gmail.com")  # Change to your verified sender
        to_email = To("rahulanand2005@gmail.com")  # Change to your recipient
        content = Content("text/plain", body)
        mail = Mail(from_email, to_email, "Test email", content).get()
        response = sg.client.mail.send.post(request_body=mail)
        return {"status_code": response.status_code}

    def convertingAgentsToTools(self):
        description = "Write a cold sales email"
        tool1 = self.sales_agents[0].as_tool(tool_name="Sales_Agent1",tool_description=description)
        tool2 = self.sales_agents[1].as_tool(tool_name="Sales_Agent2",tool_description=description)
        tool3 = self.sales_agents[2].as_tool(tool_name="Sales_Agent3",tool_description=description)
        tools = [tool1, tool2, tool3, self.sendSalesEmail]
        return tools
    
    async def salesManager(self, tools):
        instructions = """
        You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
        
        Follow these steps carefully:
        1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
        
        2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
        
        3. Use the send_email tool to send the best email (and only the best email) to the user.
        
        Crucial Rules:
        - You must use the sales agent tools to generate the drafts — do not write them yourself.
        - You must send ONE email using the send_email tool — never more than one.
        """

        sales_manager = Agent(name="Sales Manager", instructions=instructions, tools=tools, model="gpt-4o-mini")

        message = "Send a cold sales email addressed to 'Dear CEO'"

        with trace("Sales manager - Using Agents as Tools"):
            result = await Runner.run(sales_manager, message)
    
    async def main(self):
        tools = self.convertingAgentsToTools()
        await self.salesManager(tools=tools)
       
       

if __name__ == "__main__":
    manager = SalesAgentManager()
    asyncio.run(manager.main())
