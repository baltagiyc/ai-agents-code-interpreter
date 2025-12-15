from dotenv import load_dotenv
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

load_dotenv()

@tool
def triple(num: float) -> float:
    "Return the triple of the input number, the input is the number to triple"
    return float(num) * 3

tools = [TavilySearch(max_results=3), triple]

llm = ChatOpenAI(model="gpt-5", temperature=0).bind_tools(tools)

print(f"✅ react.py chargé - Tools: {[t.name for t in tools]}")
