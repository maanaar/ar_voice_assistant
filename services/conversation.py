"""Conversation session management."""
import asyncio
import os
import base64
import tempfile
import traceback
from fastapi import WebSocket
from models.tts_model import get_tts_model
import config


class ConversationSession:
    """Manages a conversation session with audio generation."""
    
    def __init__(self, pc, speaker_wav: str = None, websocket: WebSocket = None):
        """
        Initialize conversation session.
        
        Args:
            pc: RTCPeerConnection instance
            speaker_wav: Path to reference speaker audio
            websocket: WebSocket connection for updates
        """
        self.pc = pc
        self.speaker_wav = speaker_wav or config.REFERENCE_WAV
        self.websocket = websocket
        self.audio_queue = asyncio.Queue()
        self.active = True
        self.tts_model = get_tts_model()
        self._task = asyncio.create_task(self._run())
    
    async def enqueue(self, text: str):
        """Add text to speech generation queue."""
        await self.audio_queue.put(text)
    
    async def _send_ws_message(self, message: dict):
        """Send message through WebSocket."""
        if self.websocket:
            try:
                await self.websocket.send_json(message)
            except Exception as e:
                print(f"⚠️ WebSocket send failed: {e}")
    
    async def _run(self):
        """Main loop for processing audio generation queue."""
        while self.active:
            try:
                text = await self.audio_queue.get()
                
                await self._send_ws_message({
                    "type": "tts_start",
                    "text": text,
                    "text_length": len(text)
                })
                
                # Generate unique temp file
                temp_audio = os.path.join(
                    config.TEMP_DIR,
                    f"conv_{id(self.pc)}_{int(asyncio.get_event_loop().time()*1000)}.wav"
                )
                
                try:
                    # Generate TTS audio
                    self.tts_model.synthesize(
                        text=text,
                        output_path=temp_audio,
                        speaker_wav=self.speaker_wav
                    )
                    
                    file_size = os.path.getsize(temp_audio)
                    
                    # Read and encode audio as base64
                    with open(temp_audio, 'rb') as f:
                        audio_data = f.read()
                        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    print(f"📦 Sending audio: {len(audio_base64)} chars base64, {file_size} bytes")
                    
                    await self._send_ws_message({
                        "type": "tts_generated",
                        "file_size": file_size,
                        "audio_data": audio_base64
                    })
                    
                    print(f"✅ TTS audio sent to client")
                    
                except Exception as e:
                    print(f"❌ TTS generation failed: {e}")
                    traceback.print_exc()
                    await self._send_ws_message({
                        "type": "error",
                        "message": f"TTS generation failed: {str(e)}"
                    })
                    
                finally:
                    # Cleanup temp file
                    if os.path.exists(temp_audio):
                        try:
                            os.unlink(temp_audio)
                        except Exception:
                            pass
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ ConversationSession loop error: {e}")
                traceback.print_exc()
                await asyncio.sleep(0.5)
    
    async def close(self):
        """Close the conversation session."""
        self.active = False
        try:
            self._task.cancel()
            await self._task
        except Exception:
            pass
        try:
            await self.pc.close()
        except Exception:
            pass