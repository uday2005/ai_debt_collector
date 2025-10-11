from typing import TypedDict

class AgentState(TypedDict):
    messages: list[str]
    system_prompt: str
    tts_text: str
    compliance_text: str
    compliance: str
    feedback_txt: str
    end_conversation: bool
    conversation_id: str
    turn_count: int
