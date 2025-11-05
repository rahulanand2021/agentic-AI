from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel, Field
import os
from crewai_tools import SerperDevTool # type: ignore

class TrendingCompany(BaseModel):
    """A trending company in the news and is attracting attention"""
    name: str = Field(description="The name of the trending company")
    reason: str = Field(description="The reason why the company is trending in the news")
    ticker: str = Field(description="The ticker symbol of the company")

class TrendingCompanyList(BaseModel):
    """A list of trending companies in the news"""
    companies: List[TrendingCompany] = Field(description="A list of trending companies in the news")

class TrendingCompaniesResearch(BaseModel):
    """A report containing detailed analysis of each company"""
    name: str = Field(description="The name of the company")
    market_position: str = Field(description="The market position and competitive advantage of the company")
    financial_health: str = Field(description="The financial health of the company")
    future_outlook: str = Field(description="The future outlook  and growth prospects of the company")
    investment_potential: str = Field(description="The investment potential suitable for investment")

class TrendingCompaniesResearchList(BaseModel):
    """A list of reports containing detailed analysis of each company"""
    research_list: List[TrendingCompaniesResearch] = Field(description="A list of reports containing detailed analysis of each company")


@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'], # type: ignore[index]
            tools=[SerperDevTool(api_key=os.getenv('SERPER_API_KEY'))]
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'], # type: ignore[index]
            tools=[SerperDevTool(api_key=os.getenv('SERPER_API_KEY'))]
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker']
        )

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'], # type: ignore[index]
            output_pydantic=TrendingCompanyList
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'], # type: ignore[index]
            output_pydantic=TrendingCompaniesResearchList
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager
        )
