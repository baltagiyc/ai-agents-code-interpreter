import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState, StateGraph, END  # ← Bon END !
from nodes import run_agent_reasoning, tool_node

load_dotenv()

AGENT_REASON = "agent_reason"
ACT = "act"
LAST = -1


def should_continue(state: MessagesState) -> str:
    if not state["messages"][LAST].tool_calls:
        return END
    return ACT


flow = StateGraph(MessagesState)
flow.add_node(AGENT_REASON, run_agent_reasoning)
flow.add_node(ACT, tool_node)

flow.set_entry_point(AGENT_REASON)

flow.add_conditional_edges(AGENT_REASON, should_continue, {END: END, ACT: ACT})

flow.add_edge(ACT, AGENT_REASON)

app = flow.compile()

try:
    app.get_graph().draw_mermaid_png(output_file_path="flow.png")
    print("📊 Graphe sauvegardé dans flow.png")
except Exception as e:
    print(f"⚠️ Impossible de générer l'image du graphe: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🚀 Lancement de l'agent ReAct LangGraph")
    print("=" * 50 + "\n")

    result = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="C'est quoi la météo le 16/12/2025 à Paris saint-lazare ? Triple cette valeur."
                )
            ]
        }
    )

    print("\n" + "=" * 50)
    print("📤 Réponse finale:")
    print(result["messages"][-1].content)
