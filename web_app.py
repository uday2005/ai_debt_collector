import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
import uuid
import os
from typing import Dict

from ai_debt_collector.types import AgentState
from ai_debt_collector.tools.borrower_module import borrower_node
from ai_debt_collector.tools.tts_module import tts_node
from ai_debt_collector.tools.stt_module import stt_node
from ai_debt_collector.tools.compliance_module import compliance_node
from ai_debt_collector.tools.feedback_module import feedback_node

app = FastAPI()

# Serve static frontend
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def index():
    html_path = os.path.join(static_dir, 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>Frontend not found</h1>")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = websocket
        return client_id

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    def get(self, client_id: str):
        return self.active_connections.get(client_id)


manager = ConnectionManager()


async def run_simulation(ws: WebSocket, personality: str):
    # Initialize state
    state: AgentState = {
        "messages": [],
        "system_prompt": personality,
        "tts_text": "",
        "compliance_text": "",
        "compliance": "",
        "feedback_txt": "",
        "end_conversation": False,
        "conversation_id": str(uuid.uuid4()),
        "turn_count": 0,
    }

    # Conversation loop
    try:
        while not state["end_conversation"]:
            # Borrower speaks
            state = borrower_node(state)

            # Run TTS node to fill state['tts_audio_b64']
            state = tts_node(state)
            tts_b64 = state.get("tts_audio_b64", "")
            tts_text = state.get("tts_text", "")

            # Send TTS audio (base64) and text to frontend for playback
            await ws.send_json({"type": "tts", "text": tts_text, "audio_b64": tts_b64})

            # Wait for frontend to send recorded audio back (type 'audio_blob') or a stop command
            msg = await ws.receive_json()
            mtype = msg.get("type")
            if mtype == "audio_blob":
                # frontend sends base64-encoded wav bytes in 'audio_b64'
                incoming_b64 = msg.get("audio_b64", "")
                state["incoming_audio_b64"] = incoming_b64
                # if mime provided, keep it
                incoming_mime = msg.get("mime") or msg.get("audio_mime")
                if incoming_mime:
                    state["incoming_audio_mime"] = incoming_mime
                # Process STT node which will transcribe and append to messages
                state = stt_node(state)
                # After STT, borrower_node will generate the next reply in the next loop
            elif mtype == "user_utterance":
                # Optional: frontend may send text instead of audio
                user_text = msg.get("text", "")
                state["messages"].append(f"User: {user_text}")
                if any(phrase in user_text.upper() for phrase in ["END", "BYE", "GOODBYE", "I HAVE TO GO", "HANG UP", "STOP"]):
                    state["end_conversation"] = True
                    break
            elif mtype == "stop":
                state["end_conversation"] = True
                break

            state["turn_count"] += 1

        # Conversation ended: run compliance and feedback
        state = await compliance_node(state)
        state = feedback_node(state)

        # Send final analysis
        await ws.send_json({"type": "final", "compliance": state.get("compliance", ""), "feedback": state.get("feedback_txt", "")})

    except WebSocketDisconnect:
        return


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = await manager.connect(websocket)
    try:
        # First message should be 'start' with chosen personality
        init = await websocket.receive_json()
        if init.get("type") != "start":
            await websocket.send_json({"type": "error", "message": "Expected start message"})
            return
        personality = init.get("personality", "")
        # Run the simulation loop
        await run_simulation(websocket, personality)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai_debt_collector.web_app:app", host="127.0.0.1", port=8000, reload=True)
