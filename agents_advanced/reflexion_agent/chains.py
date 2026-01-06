import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

from langchain_core.output_parsers.openai_tools import (
    JsonOutputKeyToolsParser,
    JsonOutputToolsParser,
    PydanticToolsParser
)
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from schema import AnswerQuestion, ReviseAnswer

llm = ChatOpenAI(model="gpt-4o")
parser = JsonOutputToolsParser(return_id=True)
parser_pydantic = PydanticToolsParser(tools=[AnswerQuestion])

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """ You are expert researcher,
            current time: {time} 
            1. {first_instruction}
            2. reflect and critique your answer, be severe to maximize improvement
            3. recommend search queries to research information and improve your answer
            """
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Answer the user's question above using the required format."),
    
    ]
).partial(time=lambda: datetime.now().isoformat())

first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Provide a detailed around 250 words answer"
)


revise_instructions = """You are an expert researcher tasked with REVISING and IMPROVING a previous answer.

CONTEXT:
- You have access to the PREVIOUS ANSWER that was generated
- You have access to CRITICAL FEEDBACK about what was missing and what was superfluous
- You have access to LESSONS LEARNED from previous attempts (reflexion_memory)

YOUR MISSION:
1. Carefully analyze the previous answer and identify its weaknesses
2. Address ALL the missing elements mentioned in the critique
3. Remove or condense the superfluous parts identified
4. Apply the lessons learned from previous attempts (if any)
5. Generate a SIGNIFICANTLY IMPROVED version that:
   - Is more comprehensive and accurate
   - Addresses all the gaps from the critique
   - Is more concise where needed
   - Incorporates best practices from lessons learned
6. Provide a new reflection on your revised answer (be critical again)
7. Recommend new search queries if further research is needed
8. Add a "References" section to the bottom of your answer (which does not count towards the word limit)

IMPORTANT:
- Do NOT simply rephrase the previous answer
- Make SUBSTANTIVE improvements based on the critique
- Be thorough in addressing the missing elements
- Be ruthless in removing superfluous content
- Learn from past mistakes stored in reflexion_memory
"""

revisor = actor_prompt_template.partial(
    first_instruction=revise_instructions
) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")


first_responder = first_responder_prompt_template | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice="AnswerQuestion"
)


if __name__ == "__main__":
    human_message = HumanMessage(
        content="Talk me about GEO (Generative Engine Optimization) and how it's different from classic SEO, what are the best startup now working on GEO and what are the exceptations on this technology for the future ?"
    )
    chain = (
        first_responder_prompt_template
        | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
        | parser_pydantic
    )

    res = chain.invoke(input={"messages": [human_message]})
    print(res)
