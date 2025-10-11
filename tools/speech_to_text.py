import asyncio
import os
import queue
import sounddevice as sd
from dotenv import load_dotenv
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV2SocketClientResponse

# Load environment variables
load_dotenv()
api_key = os.getenv("DEEPGRAM_API_KEY")
import sys
def real_time_speech_to_text():
    """
    Performs real-time speech-to-text using Deepgram Flux via microphone input.
    
    Returns:
        str: Transcribed text when EndOfTurn is detected.
    """
    samplerate = 16000
    q = queue.Queue()
    
    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))
    
    async def transcribe():
        client = DeepgramClient(api_key = api_key)  
        transcript = ""
        done = asyncio.Event()
        
        def on_flux_message(message: ListenV2SocketClientResponse) -> None:
            nonlocal transcript
            if hasattr(message, 'type') and message.type == 'TurnInfo':
                if hasattr(message, 'event') and message.event == 'EndOfTurn':
                    if hasattr(message, 'transcript') and message.transcript:
                        transcript = message.transcript.strip()
                        print(f"✓ Transcript: '{transcript}'")
                        done.set()
        
        with client.listen.v2.connect(model="flux-general-en", encoding="linear16", sample_rate=16000) as connection:
            connection.on(EventType.MESSAGE, on_flux_message)
            
            import threading
            threading.Thread(target=connection.start_listening, daemon=True).start()
            
            with sd.RawInputStream(samplerate=samplerate, blocksize=4096, dtype='int16',
                                   channels=1, callback=callback):
                while not done.is_set():
                    data = q.get()
                    connection.send_media(data)
                    await asyncio.sleep(0.01)
                
                await asyncio.wait_for(done.wait(), timeout=30.0)
        
        return transcript
    
    return asyncio.run(transcribe())

if __name__ == "__main__":
    print("Testing real-time speech-to-text with Deepgram Flux...")
    text = real_time_speech_to_text()
    print(f"Final transcript: {text}")