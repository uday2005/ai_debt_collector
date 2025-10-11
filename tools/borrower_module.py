from langgraph.graph import StateGraph, START, END
from langchain_ollama import OllamaLLM
from ..types import AgentState

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
        return "compliance_node"
    else:
        state["tts_text"] = response
        return "tts_node"