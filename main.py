"""Main FastAPI application entry point."""
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

import config

# Import models (do NOT load them here)
from models.tts_model import get_tts_model
from models.whisper_model import get_whisper_model
from models.llm_model import get_llm_model

# Import routes
from routes.ui import get_ui
from routes.websocket import WebSocketHandler

app = FastAPI(title="Arabic Voice AI Assistant")

# WebSocket handler
ws_handler = WebSocketHandler()


@app.on_event("startup")
async def startup_event():
    """Server startup event."""
    print("🚀 Starting Arabic Voice AI Assistant...")
    print("="*60)

    print("🟢 Server started WITHOUT loading any models.")
    print("="*60)
    print(f"📍 Server ready at: http://{config.HOST}:{config.PORT}/ui")
    print("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    await ws_handler.shutdown()


@app.get("/ui")
async def ui_endpoint():
    return await get_ui()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_handler.handle_connection(websocket)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Arabic Voice AI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level="info"
    )
