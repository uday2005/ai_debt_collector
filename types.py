from typing import TypedDict

class AgentState(TypedDict):
    messages: list[str]
    system_prompt: str
    tts_text: str
    compliance: str
    compliance_tx: str
    feedback: str
    feedback_txt : str
    conversation_id: str
    turn_count: int
