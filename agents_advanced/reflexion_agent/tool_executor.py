from dotenv import load_dotenv
import sys
from pathlib import Path

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))


from langchain_tavily import TavilySearch
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import ToolNode
from schema import AnswerQuestion, ReviseAnswer

tavily_tool = TavilySearch(max_results=5)

def run_queries(search_queries: list[str], **kwargs):
    """ run the generated queries"""
    return tavily_tool.batch([{"query": query} for query in search_queries])

execute_tools = ToolNode(
    [
        StructuredTool.from_function(run_queries, name=AnswerQuestion.__name__),
        StructuredTool.from_function(run_queries, name=ReviseAnswer.__name__),
    ]
)



