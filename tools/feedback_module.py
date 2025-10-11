import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_debt_collector.types import AgentState

def feedback_node(state: AgentState) -> AgentState:
    # Mock feedback
    state["feedback_txt"] = "Mock feedback: Great job on the conversation! Keep practicing."
    return state