import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_debt_collector.tools.compliance_tool.retriever import check_compliance

def compliance_check(message: str) -> str:
    return check_compliance(message)


def compliance_node(state):
    message = state.get("compliance_text", "")
    compliance_prompt = (
    "You are training a human debt collector agent. "
    "Below is a conversation the agent has practiced. "
    "Analyze the following conversation and refer to debt collection regulations. "
    "If any part is non-compliant, clearly explain to the human agent what is wrong, "
    "how to improve, and provide specific suggestions or examples for better compliance. "
    "If the conversation is compliant, confirm this and highlight what was done well. "
    "Your goal is to help the human agent improve their compliance skills."

    )   
    if message:
        prompt = f"{compliance_prompt}\n\nConversation:\n{message}"
        result = check_compliance(prompt)
        state["compliance"] = result
    else:
        state["compliance"] = "No compliance text provided."
    return state