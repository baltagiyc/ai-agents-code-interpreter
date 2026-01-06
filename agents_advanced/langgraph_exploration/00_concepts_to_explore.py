"""
🧭 LangGraph Exploration Roadmap
================================

Concepts à explorer dans l'ordre :

1. STATE (state.py)
   - TypedDict pour définir l'état
   - Annotated avec "reducer" pour les listes
   - MessagesState (raccourci pour les messages)

2. NODES (nodes.py)
   - Fonctions qui prennent state et retournent state (ou partial)
   - Comment appeler un LLM dans un node
   - Comment appeler des tools

3. EDGES (edges.py)
   - add_edge() : transition simple
   - add_conditional_edges() : branchement
   - START et END

4. GRAPH COMPILATION
   - graph.compile()
   - Visualisation avec get_graph().draw_mermaid_png()

5. ADVANCED (quand tu maîtrises les bases)
   - Checkpointing (persistence)
   - Human-in-the-loop (interrupt)
   - Subgraphs (graphes imbriqués)
   - Streaming

📚 Ressources officielles :
- https://langchain-ai.github.io/langgraph/
- https://langchain-ai.github.io/langgraph/tutorials/
- https://github.com/langchain-ai/langgraph/tree/main/examples

💡 Tips :
- Commence par un graphe SIMPLE (2-3 nodes)
- Utilise print() partout pour voir le flow
- Visualise ton graphe à chaque étape
"""
