from langgraph.graph import StateGraph, START, END
from langchain_ollama import OllamaLLM
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_debt_collector.types import AgentState

# Initialize Ollama LLM once at module level for connection reuse
# This avoids repeated initialization overhead
llm = OllamaLLM(model="llama3.1")

def borrower_node(state: AgentState):
    """
    LLM which simulates the borrower

    Parameters:
    state (AgentState): Information of the agent which includes schema.

    Returns:
    Updated state with borrower's response set for TTS
    """
    messages = state["messages"]
    system_prompt = state["system_prompt"]
    
    # Prepare prompt with system prompt and conversation
    prompt = f"{system_prompt}\n\nConversation so far:\n" + "\n".join(messages)
    
    # Get LLM response
    response = llm.invoke(prompt).strip()
    
    state["messages"] = messages + [f"Borrower: {response}"]
    state["tts_text"] = response
        
    return state
