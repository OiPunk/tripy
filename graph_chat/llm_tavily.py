import os

from langchain_community.tools import TavilySearchResults
from langchain_openai import ChatOpenAI

# LLM configuration comes from environment variables.
# Defaults target a local OpenAI-compatible endpoint.
llm = ChatOpenAI(
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
    model=os.getenv("LLM_MODEL", "Qwen-7B"),
    openai_api_key=os.getenv("OPENAI_API_KEY", "EMPTY"),
    openai_api_base=os.getenv("OPENAI_API_BASE", "http://localhost:6006/v1"),
)

# Optional Tavily search integration.
# Set TAVILY_API_KEY in your environment if web search is required.
if os.getenv("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = os.environ["TAVILY_API_KEY"]

tavily_tool = TavilySearchResults(max_results=int(os.getenv("TAVILY_MAX_RESULTS", "1")))
