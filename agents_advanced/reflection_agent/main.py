from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from chains import generate_chain, reflect_chain

load_dotenv()


class MessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


REFLECT = "reflect"
GENERATE = "generate"


def generation_node(state: MessageGraph):
    return {"messages": [generate_chain.invoke({"messages": state["messages"]})]}


def reflection_node(state: MessageGraph):
    res = reflect_chain.invoke({"messages": state["messages"]})
    return {"messages": [HumanMessage(content=res.content)]}


def should_continue(state: MessageGraph):
    if len(state["messages"]) > 6:  # condition arbitraire pour continuer
        return END
    return REFLECT


builder = StateGraph(state_schema=MessageGraph)
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.set_entry_point(GENERATE)
builder.add_conditional_edges(
    GENERATE, should_continue, path_map={END: END, REFLECT: REFLECT}
)
builder.add_edge(REFLECT, GENERATE)

graph = builder.compile()
try:
    graph.get_graph().draw_mermaid_png(output_file_path="flow._2.png")
    print("📊 Graphe sauvegardé dans flow_2.png")
except Exception as e:
    print(f"⚠️ Impossible de générer l'image du graphe: {e}")

if __name__ == "__main__":
    print("Hello boss, let's do it")
    inputs = HumanMessage(
        content="""
    Make this tweet better: "
    Laporta a rencontré Pini Zahavi samedi dernier pour discuter de l'avenir de Lewandowski. La réunion a duré deux heures.

    L'agent a indiqué à Laporta que Lewandowski souhaitait rester une année de plus ; le joueur se sent en bonne condition physique et est impatient de continuer à jouer pour le Barça. 
    @sport
    """
    )
    response = graph.invoke({"messages": [inputs]})  # ← Dict avec clé "messages" !

    # Affichage propre du résultat final
    print("\n" + "=" * 50)
    print("🐦 TWEET FINAL:")
    print("=" * 50)
    print(response["messages"][-1].content)
