from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
from openai.types.responses import ResponseTextDeltaEvent
from openai import AsyncOpenAI
import asyncio
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from typing import Dict
from pydantic import BaseModel

class NameCheckOutput(BaseModel):
    is_name_in_message: bool
    name: str

class SalesAgentManagerHandOff:
    def __init__(self):
        self.load_api_keys()
        self.sales_agents = self.create_sales_agents()

    def load_api_keys(self):
        """Load API keys from .env"""
        load_dotenv(override=True)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')

    def create_sales_agents(self):
        """Initialize three different styles of sales agents"""
        GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
        # DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
        GROQ_BASE_URL = "https://api.groq.com/openai/v1"

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

        # deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
        gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=self.google_api_key)
        groq_client = AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=self.groq_api_key)

        # deepseek_model = OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=deepseek_client)
        gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=gemini_client)
        llama3_3_model = OpenAIChatCompletionsModel(model="llama-3.3-70b-versatile", openai_client=groq_client)

        sales_agent1 = Agent(
                name="OpenAI Sales Agent",
                instructions=instructions["Busy Sales Agent"],
                model="gpt-4o-mini"
                )

        sales_agent2 = Agent(
                name="Gemini Sales Agent",
                instructions=instructions["Engaging Sales Agent"],
                model=gemini_model
                )

        sales_agent3 = Agent(
                name="Groq Sales Agent",
                instructions=instructions["Professional Sales Agent"],
                model=llama3_3_model
                )

        return sales_agent1, sales_agent2, sales_agent3

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

    def convertingAgentsToTools(self):
        description = "Write a cold sales email"
        tool1 = self.sales_agents[0].as_tool(tool_name="Sales_Agent1",tool_description=description)
        tool2 = self.sales_agents[1].as_tool(tool_name="Sales_Agent2",tool_description=description)
        tool3 = self.sales_agents[2].as_tool(tool_name="Sales_Agent3",tool_description=description)
        tools = [tool1, tool2, tool3]
        return tools

    def createHandOffEmailerTool(self):
        subject_instructions = "You can write a subject for a cold sales email. \
        You are given a message and you need to write a subject for an email that is likely to get a response."

        html_instructions = "You can convert a text email body to an HTML email body. \
        You are given a text email body which might have some markdown \
        and you need to convert it to an HTML email body with simple, clear, compelling layout and design."

        subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")

        subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

        html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model="gpt-4o-mini")
        html_tool = html_converter.as_tool(tool_name="html_converter",tool_description="Convert a text email body to an HTML email body")

        instructions ="You are an email formatter and sender. You receive the body of an email to be sent. \
        You first use the subject_writer tool to write a subject for the email, then use the html_converter tool to convert the body to HTML. \
        Finally, you use the send_html_email tool to send the email with the subject and HTML body."

        handOff_tools = [subject_tool, html_tool, self.sendHTMLSalesEmail]

        emailer_agent = Agent(
            name="Email Manager",
            instructions=instructions,
            tools=handOff_tools,
            model="gpt-4o-mini",
            handoff_description="Convert an email to HTML and send it")

        return [emailer_agent]

    async def automatedSalesManager(self, sales_agent_tools, handOff_agent):
        sales_manager_instructions = """
        You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
        
        Follow these steps carefully:
        1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
        
        2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
        You can use the tools multiple times if you're not satisfied with the results from the first try.
        
        3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
        
        Crucial Rules:
        - You must use the sales agent tools to generate the drafts — do not write them yourself.
        - You must hand off exactly ONE email to the Email Manager — never more than one.
        """


        sales_manager = Agent(
            name="Sales Manager",
            instructions=sales_manager_instructions,
            tools=sales_agent_tools,
            handoffs=handOff_agent,
            model="gpt-4o-mini")

        message = "Send out a cold sales email addressed to Dear CEO from Alice"

        with trace("Automated SDR"):
            result = await Runner.run(sales_manager, message)

    @staticmethod
    def createGuardRailAgent():
            guardrail_agent = Agent( 
            name="Name check",
            instructions="Check if the user is including someone's personal name in what they want you to do.",
            output_type=NameCheckOutput,
            model="gpt-4o-mini")
            
            return guardrail_agent

    @input_guardrail
    @staticmethod
    async def guardrail_against_name(ctx, agent, message):
        result = await Runner.run(SalesAgentManagerHandOff.createGuardRailAgent(), message, context=ctx.context)
        is_name_in_message = result.final_output.is_name_in_message
        return GuardrailFunctionOutput(output_info={"found_name": result.final_output},tripwire_triggered=is_name_in_message)

    async def carefulSalesManagerWithGuardRails(self, sales_agent_tools, emailer_agent_handOff):

        sales_manager_instructions = """
        You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
        
        Follow these steps carefully:
        1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
        
        2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
        You can use the tools multiple times if you're not satisfied with the results from the first try.
        
        3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
        
        Crucial Rules:
        - You must use the sales agent tools to generate the drafts — do not write them yourself.
        - You must hand off exactly ONE email to the Email Manager — never more than one.
        """

        careful_sales_manager = Agent(
        name="Careful Sales Manager",
        instructions=sales_manager_instructions,
        tools=sales_agent_tools,
        handoffs=[emailer_agent_handOff],
        model="gpt-4o-mini",
        input_guardrails=[self.guardrail_against_name]
        )

        message = "Send out a cold sales email addressed to Dear CEO from Alice"

        with trace("Protected and Careful Automated SDR"):
            result = await Runner.run(careful_sales_manager, message)

    async def main(self):

        print("Getting Sale Agent tools to write Cold Emails")
        sales_tools = self.convertingAgentsToTools()

        print("Getting HandOff Agent which will send the Cold Emails")

        emailer_agent_handOff = self.createHandOffEmailerTool()

        print("Selecting the best email and sending it ...")
        await self.automatedSalesManager(sales_tools, emailer_agent_handOff)

        # Following the the code example for creating and attaching Input GuardRails
        
        # print("Executing the Careful Sales Manager with Guardrails")
        # await self.carefulSalesManagerWithGuardRails(sales_tools, emailer_agent_handOff)

if __name__ == "__main__":
    manager = SalesAgentManagerHandOff()
    asyncio.run(manager.main())
