import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_debt_collector.tools.compliance_tool.retriever import async_check_compliance


async def compliance_node(state):
    message = "\n".join(state.get("messages", []))
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
        try:
            result = await async_check_compliance(prompt)
        except Exception as e:
            result = f"Compliance check failed: {e}"
        state["compliance"] = result
    else:
        state["compliance"] = "No compliance text provided."
    return state