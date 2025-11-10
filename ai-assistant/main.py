"""
AI Multitask Assistant - Main Application
FastAPI server with bilingual support (English/Urdu)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from .core.config import settings
from .core.database import init_db
from .api import tasks, assistant, files, n8n, whatsapp, voice, learning

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered multitasking assistant with bilingual support (English/Urdu), WhatsApp, Voice, and Smart Learning & Personalization",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assistant.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(files.router, prefix="/api/v1")
app.include_router(n8n.router, prefix="/api/v1")
app.include_router(whatsapp.router, prefix="/api/v1")
app.include_router(voice.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    return """
    <html>
        <head>
            <title>AI Multitask Assistant</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>🤖 AI Multitask Assistant</h1>
            <p>Bilingual AI Assistant (English/Urdu) for multitasking and automation</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/redoc">ReDoc Documentation</a></li>
            </ul>
            <h2>Quick Start</h2>
            <p>Use the <code>/api/v1/assistant</code> endpoint to interact with the assistant in natural language.</p>
            <h3>Example (English):</h3>
            <pre>
POST /api/v1/assistant
{
    "message": "Create a task to buy groceries tomorrow",
    "language": "en"
}
            </pre>
            <h3>Example (Urdu):</h3>
            <pre>
POST /api/v1/assistant
{
    "message": "کل گروسری خریدنے کا کام بنائیں",
    "language": "ur"
}
            </pre>
        </body>
    </html>
    """


@app.get("/api/v1/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
