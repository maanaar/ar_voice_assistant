"""Main FastAPI application entry point."""
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

# Import configuration
import config

# Import models to initialize them
from models.tts_model import get_tts_model
from models.whisper_model import get_whisper_model
from models.llm_model import get_llm_model

# Import route handlers
from routes.ui import get_ui
from routes.websocket import WebSocketHandler


# Initialize FastAPI app
app = FastAPI(title="Arabic Voice AI Assistant")

# Mount static files (if you have CSS/JS)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize WebSocket handler
ws_handler = WebSocketHandler()


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    print("🚀 Starting Arabic Voice AI Assistant...")
    print("="*60)
    
    # Preload models
    get_tts_model()
    get_whisper_model()
    get_llm_model()
    
    print("="*60)
    print(f"📍 Server ready at: http://{config.HOST}:{config.PORT}/ui")
    print("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await ws_handler.shutdown()


@app.get("/ui")
async def ui_endpoint():
    """Serve the main UI."""
    return await get_ui()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await ws_handler.handle_connection(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Arabic Voice AI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config.HOST, 
        port=config.PORT,
        log_level="info"
    )