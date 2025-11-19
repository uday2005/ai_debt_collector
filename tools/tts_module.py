import io
import os
import wave
import sys
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from piper import PiperVoice
from ai_debt_collector.types import AgentState

# Synthesize to WAV bytes and attach base64 audio to state so the web frontend can play it.
try:
    # load the compiled piper model (path may vary). Keep as JSON path if that's what you use.
    voice = PiperVoice.load("/Users/uday/Desktop/hackathon/en_US-lessac-medium.onnx")
    print("TTS initialized Successfully")
except Exception as e:
    print(f"TTS initialization failed: {e}")
    voice = None


def tts_node(state: AgentState) -> AgentState:
    """Text-to-speech node that places base64 WAV audio in state['tts_audio_b64'].

    This avoids playing audio on the server and lets the frontend play the audio blob.
    Optimized to use in-memory BytesIO instead of temp files.
    """
    text = state.get("tts_text", "")

    # Clear any previous audio
    state["tts_audio_b64"] = ""

    if not text:
        return state

    # If piper voice isn't available, keep text and return
    if not voice:
        print("TTS voice not available; returning text-only")
        state["tts_audio_b64"] = ""
        return state

    try:
        # Use in-memory BytesIO instead of temp file for better performance
        audio_buffer = io.BytesIO()
        
        # Create wave file in memory
        with wave.open(audio_buffer, "wb") as wf:
            # PiperVoice.synthesize_wav expects a wave file-like object opened for writing
            voice.synthesize_wav(text, wf)
        
        # Get bytes from buffer
        audio_bytes = audio_buffer.getvalue()
        state["tts_audio_b64"] = base64.b64encode(audio_bytes).decode("ascii")

        # keep tts_text for debugging/legacy uses
        state["tts_text"] = text

    except Exception as e:
        print(f"TTS error: {e}; leaving text-only output")
        state["tts_audio_b64"] = ""

    return state

