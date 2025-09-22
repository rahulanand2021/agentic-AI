from dotenv import load_dotenv
from agents import Agent, Runner, trace
from openai.types.responses import ResponseTextDeltaEvent
import asyncio


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

    async def run_agent(self, agent_name, message="Write a cold sales email"):
        """Run a single agent with streaming output"""
        sales_agent = self.sales_agents[agent_name]
        result = Runner.run_streamed(sales_agent, input=message)

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)

    async def run_parallel_agents(self, message="Write a cold sales email"):
        """Run all agents in parallel and print outputs"""
        with trace("Parallel cold emails"):
            results = await asyncio.gather(
                        Runner.run(self.sales_agents[0], message),
                        Runner.run(self.sales_agents[1], message),
                        Runner.run(self.sales_agents[2], message),
            )

        self.outputs = [result.final_output for result in results]
        for output in self.outputs:
            print(output + "\n\n")

    async def best_email_picker(self, outputs=None ) :
        
        print("Picking the Best Email ... Please Stand By ..")
        
        sales_picker = Agent(
        name="sales_picker",
        instructions="You pick the best cold sales email from the given options. \
        Imagine you are a customer and pick the one you are most likely to respond to. \
        Do not give an explanation; reply with the selected email only.",
        model="gpt-4o-mini"
        )

        if outputs is None:
            allEmail = self.outputs
        else :
            allEmail = outputs

        emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(allEmail)

        best = await Runner.run(sales_picker, emails)

        print(f"Best sales email:\n{best.final_output}")

    async def main(self):
        await self.run_parallel_agents()
        await self.best_email_picker()

if __name__ == "__main__":
    manager = SalesAgentManager()

    # Run single agent (streaming)
    # asyncio.run(manager.run_agent("Professional Sales Agent"))

    asyncio.run(manager.main())
