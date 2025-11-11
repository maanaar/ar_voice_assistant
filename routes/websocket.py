import os
import tempfile
import traceback
from fastapi import WebSocket, WebSocketDisconnect
from aiortc import RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

from services.conversation import ConversationSession
from services.audio_processor import get_audio_processor
from models.tts_model import get_tts_model
from models.llm_model import get_llm_model
from utils.webrtc import create_rtc_configuration, parse_ice_candidate
import config

"""WebSocket route handlers."""
import os
import tempfile
import traceback
from fastapi import WebSocket, WebSocketDisconnect
from aiortc import RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

from services.conversation import ConversationSession
from services.audio_processor import get_audio_processor
from models.tts_model import get_tts_model
from models.llm_model import get_llm_model
from utils.webrtc import create_rtc_configuration, parse_ice_candidate
import config


class WebSocketHandler:
    """Handles WebSocket connections and messages."""
    
    def __init__(self):
        """Initialize handler."""
        self.pcs = set()
        self.audio_processor = get_audio_processor()
        self.tts_model = get_tts_model()
        self.llm_model = get_llm_model()
    
    async def handle_connection(self, websocket: WebSocket):
        """Handle WebSocket connection lifecycle."""
        await websocket.accept()
        log_id = id(websocket)
        print(f"🔌 WebSocket connected: {log_id}")
        
        pc = None
        session = None
        
        try:
            while True:
                data = await websocket.receive_json()
                await self._handle_message(data, websocket, pc, session)
                
        except WebSocketDisconnect:
            print(f"🔌 WebSocket disconnected: {log_id}")
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            traceback.print_exc()
        finally:
            await self._cleanup(pc, session)
    
    async def _handle_message(self, data: dict, websocket: WebSocket, pc, session):
        """Route message to appropriate handler."""
        msg_type = data.get("type")
        print(f"📨 Received: {msg_type}")
        
        if msg_type == "webrtc_offer":
            pc, session = await self._handle_webrtc_offer(data, websocket)
            return pc, session
        
        elif msg_type == "ice_candidate":
            await self._handle_ice_candidate(data, pc)
        
        elif msg_type == "renegotiate_answer":
            await self._handle_renegotiate_answer(data, pc)
        
        elif msg_type == "voice_input":
            await self._handle_voice_input(data, websocket, session)
        
        return pc, session
    
    async def _handle_webrtc_offer(self, data: dict, websocket: WebSocket):
        """Handle WebRTC offer and setup connection."""
        try:
            text = data.get("text", "")
            offer_data = data.get("offer")
            
            offer = RTCSessionDescription(
                sdp=offer_data["sdp"],
                type=offer_data["type"]
            )
            
            pc = create_rtc_configuration()
            self.pcs.add(pc)
            
            # Text mode: generate TTS immediately
            if text.strip():
                print(f"📝 Text mode - synthesizing: '{text}'")
                temp_audio = os.path.join(
                    config.TEMP_DIR, 
                    f"output_{id(pc)}.wav"
                )
                
                self.tts_model.synthesize(
                    text=text,
                    output_path=temp_audio
                )
                player = MediaPlayer(temp_audio)
                pc.addTrack(player.audio)
            else:
                print("🎤 Voice mode - WebRTC connection established")
            
            # Create conversation session
            session = ConversationSession(
                pc, 
                speaker_wav=config.REFERENCE_WAV, 
                websocket=websocket
            )
            pc.session = session
            
            # Setup event handlers
            self._setup_pc_handlers(pc, session)
            
            # Complete WebRTC handshake
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            
            await websocket.send_json({
                "type": "sdp_answer",
                "answer": {
                    "sdp": pc.localDescription.sdp,
                    "type": pc.localDescription.type
                }
            })
            print("✅ SDP answer sent")
            
            return pc, session
            
        except Exception as e:
            print(f"❌ Error handling offer: {e}")
            traceback.print_exc()
            await websocket.send_json({"type": "error", "message": str(e)})
            return None, None
    
    async def _handle_ice_candidate(self, data: dict, pc):
        """Handle ICE candidate."""
        if not pc:
            return
        
        candidate = parse_ice_candidate(data.get("candidate"))
        if candidate:
            try:
                await pc.addIceCandidate(candidate)
                print("✅ ICE candidate added")
            except Exception as e:
                print(f"⚠️ Failed to add ICE candidate: {e}")
    
    async def _handle_renegotiate_answer(self, data: dict, pc):
        """Handle renegotiation answer."""
        if not pc:
            return
        
        try:
            answer_data = data.get("answer")
            answer = RTCSessionDescription(
                sdp=answer_data["sdp"],
                type=answer_data["type"]
            )
            await pc.setRemoteDescription(answer)
            print("✅ Renegotiation completed")
        except Exception as e:
            print(f"❌ Renegotiation failed: {e}")
            traceback.print_exc()
    
    async def _handle_voice_input(self, data: dict, websocket: WebSocket, session):
        """Handle voice input processing."""
        try:
            print("🎤 Processing voice input...")
            
            # Transcribe audio
            text_input = await self.audio_processor.process_audio_input(
                data.get("audio")
            )
            
            await websocket.send_json({
                "type": "transcription", 
                "text": text_input
            })
            
            if not text_input.strip():
                await websocket.send_json({
                    "type": "error", 
                    "message": "No speech detected"
                })
                return
            
            # Generate LLM response
            response_text = await self.llm_model.generate_response(text_input)
            await websocket.send_json({
                "type": "llm_response", 
                "text": response_text
            })
            
            # Queue TTS
            if session:
                await session.enqueue(response_text)
                print("💬 Response enqueued for playback")
            else:
                print("⚠️ No active session for TTS playback")
                
        except Exception as e:
            print(f"❌ Error processing voice: {e}")
            traceback.print_exc()
            await websocket.send_json({
                "type": "error", 
                "message": str(e)
            })
    
    def _setup_pc_handlers(self, pc, session):
        """Setup peer connection event handlers."""
        
        @pc.on("datachannel")
        def on_datachannel(channel):
            print(f"📡 Data channel: {channel.label}")
            
            @channel.on("message")
            def on_message(message):
                if isinstance(message, str) and message == "ping":
                    try:
                        channel.send("pong")
                    except Exception as e:
                        print(f"Pong failed: {e}")
        
        @pc.on("iceconnectionstatechange")
        async def on_ice_state():
            print(f"🧊 ICE state: {pc.iceConnectionState}")
        
        @pc.on("connectionstatechange")
        async def on_connection_state():
            print(f"🔗 Connection state: {pc.connectionState}")
            if pc.connectionState == "failed":
                print("⚠️ Connection failed")
                if session:
                    await session.close()
                await pc.close()
                self.pcs.discard(pc)
    
    async def _cleanup(self, pc, session):
        """Cleanup resources."""
        if session:
            await session.close()
        if pc:
            await pc.close()
            self.pcs.discard(pc)
    
    async def shutdown(self):
        """Shutdown all connections."""
        print("🛑 Shutting down WebSocket handler...")
        coros = []
        for pc in list(self.pcs):
            if hasattr(pc, "session"):
                coros.append(pc.session.close())
            else:
                coros.append(pc.close())
        
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)
        self.pcs.clear()
        print("✅ All connections closed")