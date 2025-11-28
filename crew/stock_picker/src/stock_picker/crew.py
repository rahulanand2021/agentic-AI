from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel, Field
import os
from crewai_tools import SerperDevTool # type: ignore
from stock_picker.tools.push_tool import PushNotificationTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage



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
            tools=[SerperDevTool(api_key=os.getenv('SERPER_API_KEY'))],
            memory=True
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
            config=self.agents_config['stock_picker'],
            tools=[PushNotificationTool()],
            memory=True
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

        # Set CHROMA_OPENAI_API_KEY from OPENAI_API_KEY if not already set
        # This is required by ChromaDB when using OpenAI embeddings
        if not os.getenv('CHROMA_OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY'):
            os.environ['CHROMA_OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

        # Long-term memory for persistent storage across sessions
        long_term_memory = LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path="./memory/long_term_memory_storage.db"
            )
        )
        
        # Short-term memory for current context using RAG
        short_term_memory = ShortTermMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai"
                },
                type="short_term",
                path="./memory/short_term_memory"
            )
        )
        
        # Entity memory for tracking key information about entities
        entity_memory = EntityMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider": "openai"
                },
                type="entity",
                path="./memory/entity_memory"
            )
        )


        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            short_term_memory=short_term_memory,
            long_term_memory=long_term_memory,
            entity_memory=entity_memory
        )
