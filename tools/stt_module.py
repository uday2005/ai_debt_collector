import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_debt_collector.tools.speech_to_text import real_time_speech_to_text

def stt_node(state):
    """
    STT node that listens for user speech and adds it to the conversation.
    
    Args:
        state (AgentState): The current state of the agent.
    
    Returns:
        dict: Updated state with the user's speech added to messages.
    """
    print("Listening for user input...")
    user_text = real_time_speech_to_text()
    if user_text:
        new_message = f"User: {user_text}"
        print(f"User said: {user_text}")
        state["messages"].append(new_message)
        state["tts_text"] = ""
    else:
        print("No speech detected.")
    return state
