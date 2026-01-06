# =============================================================================
# EXEMPLE CONCRET : ASSISTANT DE RECHERCHE AVEC STATE CUSTOM
# =============================================================================
#
# CAS D'USAGE RÉEL : Tu poses une question, l'agent :
# 1. Cherche sur le web (Tavily)
# 2. Analyse les sources trouvées
# 3. Génère un rapport structuré
#
# Le State custom permet de tracker :
# - Combien de recherches ont été faites
# - Quelles sources ont été consultées
# - L'évolution de la réponse
# =============================================================================

import sys
from pathlib import Path
from typing import TypedDict, Annotated
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_tavily import TavilySearch

# =============================================================================
# 1. STATE CUSTOM - On définit TOUT ce qu'on veut tracker
# =============================================================================


class ResearchState(TypedDict):
    """
    Notre State personnalisé pour l'agent de recherche.

    Pourquoi pas juste MessagesState ?
    → Parce qu'on veut VOIR ce qui se passe :
      combien de recherches, quelles sources, quelle confiance...
    """

    # La conversation (messages LLM) - avec add_messages pour accumuler
    messages: Annotated[list[BaseMessage], add_messages]

    # La question originale de l'utilisateur
    user_question: str

    # Les sources trouvées par Tavily
    sources_found: list[dict]  # [{url, title, content}, ...]

    # Compteur de recherches effectuées
    search_count: int

    # Le résumé final généré
    final_summary: str

    # Score de confiance (1-10)
    confidence_score: int

    # Étape actuelle pour debug
    current_step: str


# =============================================================================
# 2. CONFIGURATION
# =============================================================================

# Le LLM pour analyser et rédiger
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Le tool de recherche web
tavily = TavilySearch(max_results=3)


# =============================================================================
# 3. LES NODES - Chaque étape du workflow
# =============================================================================


def recherche_web(state: ResearchState) -> dict:
    """
    NODE 1 : Fait une recherche web avec Tavily.

    Entrée : La question de l'utilisateur
    Sortie : Liste de sources avec leurs contenus
    """
    print(f"\n🔍 RECHERCHE WEB pour : '{state['user_question']}'")

    # Appel à Tavily
    results = tavily.invoke(state["user_question"])

    # Tavily retourne une string, on la parse
    # En vrai, TavilySearch retourne directement les résultats structurés
    # mais pour l'exemple on simule la structure

    sources = []
    if isinstance(results, str):
        # Si c'est une string, on crée une source fictive
        sources = [{"url": "tavily_search", "title": "Résultats", "content": results}]
    elif isinstance(results, list):
        sources = results
    else:
        sources = [{"url": "unknown", "title": "Résultat", "content": str(results)}]

    print(f"   ✅ {len(sources)} source(s) trouvée(s)")
    for i, src in enumerate(sources[:3]):
        if isinstance(src, dict):
            print(f"   {i+1}. {src.get('title', src.get('url', 'Source'))[:50]}...")

    # On retourne les modifications du State
    return {
        "sources_found": sources,
        "search_count": state["search_count"] + 1,
        "current_step": "recherche_terminée",
        "messages": [
            AIMessage(content=f"J'ai trouvé {len(sources)} source(s) pertinente(s).")
        ],
    }


def analyse_sources(state: ResearchState) -> dict:
    """
    NODE 2 : Analyse les sources avec le LLM.

    Entrée : Les sources trouvées
    Sortie : Un score de confiance et une analyse
    """
    print(f"\n🧠 ANALYSE des {len(state['sources_found'])} sources...")

    # Prépare le contexte pour le LLM
    sources_text = "\n\n".join(
        [
            f"Source {i+1}:\n{src.get('content', str(src))[:500]}"
            for i, src in enumerate(state["sources_found"][:3])
        ]
    )

    analysis_prompt = f"""Analyse ces sources pour répondre à la question : "{state['user_question']}"

SOURCES :
{sources_text}

Réponds en JSON avec ce format :
{{"confidence": 1-10, "key_facts": ["fait 1", "fait 2"], "analysis": "ton analyse"}}
"""

    response = llm.invoke(
        [
            SystemMessage(
                content="Tu es un analyste expert. Réponds uniquement en JSON valide."
            ),
            HumanMessage(content=analysis_prompt),
        ]
    )

    # Parse basique (en prod tu utiliserais un parser JSON)
    content = response.content

    # Extraire la confiance (simpliste)
    confidence = 7  # Par défaut
    if '"confidence":' in content:
        try:
            import re

            match = re.search(r'"confidence":\s*(\d+)', content)
            if match:
                confidence = int(match.group(1))
        except:
            pass

    print(f"   ✅ Analyse terminée - Confiance : {confidence}/10")

    return {
        "confidence_score": confidence,
        "current_step": "analyse_terminée",
        "messages": [
            AIMessage(
                content=f"Analyse terminée. Confiance : {confidence}/10\n{content}"
            )
        ],
    }


def genere_rapport(state: ResearchState) -> dict:
    """
    NODE 3 : Génère le rapport final.

    Entrée : L'analyse et les sources
    Sortie : Un résumé structuré
    """
    print(f"\n📝 GÉNÉRATION du rapport final...")

    rapport_prompt = f"""Question originale : {state['user_question']}

Basé sur {len(state['sources_found'])} sources analysées avec une confiance de {state['confidence_score']}/10.

Génère un rapport structuré avec :
1. **Réponse courte** (2-3 phrases)
2. **Points clés** (liste à puces)
3. **Limites** (ce qu'on ne sait pas)

Sois concis et factuel.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content="Tu es un rédacteur expert. Structure tes réponses clairement."
            ),
            HumanMessage(content=rapport_prompt),
        ]
    )

    print(f"   ✅ Rapport généré ({len(response.content)} caractères)")

    return {
        "final_summary": response.content,
        "current_step": "rapport_généré",
        "messages": [response],
    }


# =============================================================================
# 4. CONDITIONS - Logique de décision
# =============================================================================


def faut_il_reanalyser(state: ResearchState) -> str:
    """
    Décide si on doit refaire une analyse ou passer au rapport.

    Logique :
    - Si confiance < 5 ET moins de 2 recherches → refaire une recherche
    - Sinon → générer le rapport
    """
    print(
        f"\n🤔 DÉCISION : Confiance={state['confidence_score']}, Recherches={state['search_count']}"
    )

    if state["confidence_score"] < 5 and state["search_count"] < 2:
        print("   → Confiance trop basse, nouvelle recherche")
        return "recherche"

    print("   → Confiance OK, génération du rapport")
    return "rapport"


# =============================================================================
# 5. CONSTRUCTION DU GRAPH
# =============================================================================

# Création avec notre State custom
graph = StateGraph(ResearchState)

# Ajout des nodes (chaque étape)
graph.add_node("recherche", recherche_web)
graph.add_node("analyse", analyse_sources)
graph.add_node("rapport", genere_rapport)

# Point d'entrée : on commence par la recherche
graph.set_entry_point("recherche")

# Après recherche → toujours analyse
graph.add_edge("recherche", "analyse")

# Après analyse → décision (refaire recherche ou générer rapport)
graph.add_conditional_edges(
    "analyse",
    faut_il_reanalyser,
    {
        "recherche": "recherche",  # Boucle si confiance basse
        "rapport": "rapport",  # Sinon rapport final
    },
)

# Après rapport → FIN
graph.add_edge("rapport", END)

# Compilation
app = graph.compile()

# Sauvegarde du graph en image
try:
    app.get_graph().draw_mermaid_png(output_file_path="research_agent_flow.png")
    print("📊 Graph sauvegardé dans research_agent_flow.png")
except Exception as e:
    print(f"⚠️ Impossible de générer l'image : {e}")


# =============================================================================
# 6. EXÉCUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AGENT DE RECHERCHE - Exemple avec State Custom")
    print("=" * 60)

    # La question de l'utilisateur
    question = "Quels sont les derniers développements de LangGraph en décembre 2024 ?"

    # STATE INITIAL - C'est TOI qui initialises tous les champs
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "user_question": question,
        "sources_found": [],  # Vide au départ
        "search_count": 0,  # Pas encore de recherche
        "final_summary": "",  # Pas encore de résumé
        "confidence_score": 0,  # Pas encore de score
        "current_step": "démarrage",  # Étape initiale
    }

    print(f"\n📋 Question : {question}")
    print("-" * 60)

    # Exécution de l'agent
    result = app.invoke(initial_state)

    # ==========================================================================
    # AFFICHAGE DU RÉSULTAT - Grâce au State custom, on a TOUT
    # ==========================================================================

    print("\n" + "=" * 60)
    print("📊 RÉSULTAT FINAL")
    print("=" * 60)

    print(f"\n🔢 Statistiques :")
    print(f"   • Recherches effectuées : {result['search_count']}")
    print(f"   • Sources trouvées : {len(result['sources_found'])}")
    print(f"   • Score de confiance : {result['confidence_score']}/10")
    print(f"   • Étape finale : {result['current_step']}")
    print(f"   • Messages générés : {len(result['messages'])}")

    print(f"\n📝 Rapport final :")
    print("-" * 60)
    print(result["final_summary"])

    print("\n" + "=" * 60)
    print("💡 AVEC MessagesState, tu n'aurais eu QUE les messages,")
    print("   pas les stats, pas les sources, pas le score de confiance !")
    print("=" * 60)
