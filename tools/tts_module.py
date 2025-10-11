import tempfile
import os
import wave
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from piper import PiperVoice
from ai_debt_collector.types import AgentState

# import platform

# def play_audio_cross_platform(file_path: str):
#     """Play audio file on any platform"""
#     system = platform.system().lower()
    
#     if system == "windows":
#         import winsound
#         winsound.PlaySound(file_path, winsound.SND_FILENAME)
#     elif system == "darwin":  # macOS
#         os.system(f"afplay {file_path}")
#     elif system == "linux":
#         os.system(f"aplay {file_path}")  # or use pygame.mixer
#     else:
#         print(f"Unsupported platform: {system}")

try:
    voice = PiperVoice.load("/Users/uday/Desktop/hackathon/en_US-lessac-medium.onnx")
    print("TTS intialized Succesfully")
except Exception as e:
    print(f" TTS intialization failed: {e} ")
    voice = None
    
    
def tts_node(state: AgentState) -> AgentState:
    """ Text-to-speech processing node"""
    text  = state.get("tts_text","")
    
    if text and voice:
        print(f"Agent (text) : {text}")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file_path = temp_file.name
                with wave.open(temp_file_path, "wb") as wave_file:
                    voice.synthesize_wav(text, wave_file)
            os.system(f"afplay {temp_file_path}")
            os.unlink(temp_file_path)
        except Exception as e:
            print("TTS error : {e} Text output only")
            
    return state

