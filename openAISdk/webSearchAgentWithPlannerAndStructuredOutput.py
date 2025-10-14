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
