import asyncio
import uuid
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from langgraph.graph import StateGraph, START, END
from ai_debt_collector.types import AgentState

from ai_debt_collector.tools.tts_module import tts_node
from ai_debt_collector.tools.compliance_module import compliance_node
from ai_debt_collector.tools.borrower_module import borrower_node
from ai_debt_collector.tools.stt_module import stt_node
from ai_debt_collector.tools.feedback_module import feedback_node

# Define the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("borrower", borrower_node)
graph.add_node("tts", tts_node)
graph.add_node("stt", stt_node)
graph.add_node("compliance", compliance_node)
graph.add_node("feedback", feedback_node)  # Mock for now

# Add edges
graph.add_edge(START, "borrower")
graph.add_conditional_edges(
    "borrower",
    lambda state: "compliance" if state.get("end_conversation") else "tts",
    {"tts": "tts", "compliance": "compliance"}
)
graph.add_edge("tts", "stt")  # Assuming tts outputs to user, then user input to stt
graph.add_edge("stt", "borrower")
graph.add_edge("compliance", "feedback")
graph.add_edge("feedback", END)

# Compile the graph
agent = graph.compile()

# Function to run the agent (for training simulation)
async def run_agent(personality: str):
    initial_state = AgentState(
        messages=[],
        system_prompt=personality,
        tts_text="",
        compliance_text="",
        compliance="",
        feedback_txt="",
        end_conversation=False,
        conversation_id=str(uuid.uuid4()),
        turn_count=0
    )
    result = await agent.ainvoke(initial_state)
    return result

if __name__ == "__main__":
    # personality is chosen in frontend by the user
    personality = "You are a borrower who is polite but firm. "
    "You owe $500 and can pay $100/month, your are short tempered. "
    "Keep your responses real. If you feel the conversation is about to "
    "end someting like bye, or else something like that, then just reply with 'END', nothing else"
    result = asyncio.run(run_agent(personality))
    print(result['compliance'])