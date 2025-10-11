from langgraph.graph import StateGraph, START, END
from langchain_ollama import OllamaLLM
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_debt_collector.types import AgentState

# Initialize Ollama LLM
llm = OllamaLLM(model="llama3.1")

def borrower_node(state: AgentState):
    """
    LLM which simulates the borrower

    Parameters:
    state (AgentState): Information of the agent which includes schema.

    Returns:
    Conditionally calls TTS or else END
    """
    messages = state["messages"]
    system_prompt = state["system_prompt"]
    
    # Prepare prompt with system prompt and conversation
    prompt = f"{system_prompt}\n\nConversation so far:\n" + "\n".join(messages)
    
    # Get LLM response
    response = llm.invoke(prompt).strip()
    
    state["messages"] = messages + [f"Agent: {response}"]
    state["system_prompt"] = system_prompt
    # If response is "END", end; else, set for TTS
    if response.upper() == "END":
        print("Agent: END")
        state["tts_text"] = ""
        state["end_conversation"] = True
        state["compliance_text"] = "\n".join(state["messages"])
    else:
        state["tts_text"] = response
        state["end_conversation"] = False
    return state