from pathlib import Path

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_experimental.tools import PythonREPLTool
from langchain_experimental.agents import create_csv_agent
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

SCRIPT_DIR = Path(__file__).parent


def main():
    print("start...")

    llm = ChatOpenAI(temperature=0, model="gpt-4o")

    # agent python
    python_agent_instructions = """You are a Python code execution agent. 
    IMPORTANT: You MUST use the python_repl tool to execute code. Never just describe code - EXECUTE it.
    
    You have access to:
    - qrcode package for generating QR codes
    - All standard Python libraries
    
    Rules:
    1. ALWAYS execute code using the python_repl tool
    2. If you get an error, debug and retry
    3. After execution, report what was done based on the actual output
    4. Files are saved in the current working directory
    """

    python_agent_executor = create_react_agent(
        model=llm,
        tools=[PythonREPLTool()],
        prompt=python_agent_instructions,
    )

    # agent csv
    csv_agent_executor = create_csv_agent(
        llm=llm,
        path=str(SCRIPT_DIR / "projets_lpb.csv"),
        verbose=True,
        allow_dangerous_code=True,
    )

    # agent rooter
    def run_python_agent(query: str) -> str:
        """Wrapper pour adapter l'API LangGraph vers string"""
        result = python_agent_executor.invoke({"messages": [("human", query)]})
        return result["messages"][-1].content

    def run_csv_agent(query: str) -> str:
        """Wrapper pour adapter l'ancienne API vers string"""
        result = csv_agent_executor.invoke({"input": query})
        return result["output"]

    # the description of each tool is very important
    # without that, the rooter agent will not now which tool use
    router_tools = [
        Tool(
            name="python_agent",
            func=run_python_agent,
            description="Useful when you need to transform natural language to python and execute python code, returning the results of the code execution. DOES NOT ACCEPT CODE AS INPUT.",
        ),
        Tool(
            name="csv_agent",
            func=run_csv_agent,
            description="Useful when you need to answer questions over the CSV file 'projets_lpb.csv'. Takes the entire question as input and returns the answer after running pandas calculations.",
        ),
    ]

    router_instructions = """You are a supervisor agent that delegates tasks to specialized agents.
    You have access to:
    - python_agent: for executing Python code
    - csv_agent: for analyzing CSV data
    
    Choose the right agent based on the user's question.
    """

    router_agent = create_react_agent(
        model=llm,
        tools=router_tools,
        prompt=router_instructions,
    )

    result = router_agent.invoke(
        {
            "messages": [
                (
                    "human",
                    "génère 2 qr codes qui envoie sur la page https://www.linkedin.com/in/yacin-christian-baltagi/, tu as accès à la bibliotheque python qr code, sauvegarde les images dans le répertoire courant",
                )
            ]
            # "Quel est le type de projet qui revient le plus souvent ?"
        }
    )

    print("\n" + "=" * 50)
    print("FINAL RESPONSE:")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
