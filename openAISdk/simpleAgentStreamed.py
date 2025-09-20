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

        outputs = [result.final_output for result in results]
        for output in outputs:
            print(output + "\n\n")


if __name__ == "__main__":
    manager = SalesAgentManager()

    # Run single agent (streaming)
    # asyncio.run(manager.run_agent("Professional Sales Agent"))

    # Run all in parallel
    asyncio.run(manager.run_parallel_agents())
