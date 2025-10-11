import os
import sys
import base64
import tempfile
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai_debt_collector.types import AgentState

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


def transcribe_wav_bytes_via_deepgram(audio_bytes: bytes, mime: str = "audio/wav") -> str:
    """Send WAV bytes to Deepgram speech-to-text REST endpoint and return transcript.

    Requires DEEPGRAM_API_KEY in env.
    """
    if not DEEPGRAM_API_KEY:
        print("DEEPGRAM_API_KEY not set; cannot transcribe")
        return ""

    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": mime,
    }
    try:
        resp = requests.post(url, headers=headers, data=audio_bytes, params={"punctuate": "true"}, timeout=30)
        resp.raise_for_status()
        j = resp.json()
        # Deepgram returns transcripts in 'results.channels[0].alternatives[0].transcript'
        transcript = ""
        if "results" in j and "channels" in j["results"] and j["results"]["channels"]:
            ch = j["results"]["channels"][0]
            if ch.get("alternatives"):
                transcript = ch["alternatives"][0].get("transcript", "").strip()
        # fallback older shape
        if not transcript:
            transcript = j.get("metadata", {}).get("transcript", "")
        return transcript
    except Exception as e:
        print(f"Deepgram transcription error: {e}")
        return ""


def stt_node(state: AgentState) -> AgentState:
    """STT node updated to accept base64 WAV sent from frontend in state['incoming_audio_b64'].

    If present, it will transcribe and append to state['messages'] and set
    state['last_user_transcript'].
    """
    incoming_b64 = state.get("incoming_audio_b64", "")
    state["last_user_transcript"] = ""

    if not incoming_b64:
        # No incoming audio to transcribe; keep behavior non-blocking
        return state

    try:
        wav_bytes = base64.b64decode(incoming_b64)
    except Exception as e:
        print(f"Failed to decode incoming audio b64: {e}")
        return state

    # Determine mime type if provided in state
    mime = state.get("incoming_audio_mime", "audio/wav")

    # Transcribe via Deepgram
    transcript = transcribe_wav_bytes_via_deepgram(wav_bytes, mime)
    if transcript:
        print(f"STT recognized: {transcript}")
        state["messages"].append(f"User: {transcript}")
        state["last_user_transcript"] = transcript
        # Basic end detection
        if any(phrase in transcript.upper() for phrase in ["END", "BYE", "GOODBYE", "I HAVE TO GO", "HANG UP", "STOP"]):
            state["end_conversation"] = True

    # clear incoming audio after processing
    state["incoming_audio_b64"] = ""
    return state
