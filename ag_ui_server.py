#!/usr/bin/env python3
"""
AG-UI compatible server for CrewAI SEO Analysis System
Enhanced with real-time event streaming for interactive experience
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import the main SEO analysis system
from main import SEOAnalysisSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="CrewAI SEO Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class AnalysisRequest(BaseModel):
    url: str
    session_id: str = "default"

# Global SEO system instance
seo_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize the SEO analysis system on startup"""
    global seo_system
    try:
        seo_system = SEOAnalysisSystem()
        logger.info("SEO Analysis System initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize SEO system: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze")
async def analyze_website(request: AnalysisRequest):
    """Analyze a website for SEO"""
    try:
        if not seo_system:
            raise HTTPException(status_code=500, detail="SEO system not initialized")
        
        result = seo_system.analyze_website(request.url)
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    """Chat endpoint for AG-UI compatibility"""
    return StreamingResponse(
        chat_stream(message.message, message.session_id),
        media_type="text/plain"
    )

async def chat_stream(user_message: str, session_id: str) -> AsyncGenerator[str, None]:
    """Stream chat responses with AG-UI events"""
    try:
        # Detect if the message contains a URL for SEO analysis
        if "http" in user_message.lower() or "www." in user_message.lower():
            # Extract URL from message
            words = user_message.split()
            url = None
            for word in words:
                if word.startswith(('http://', 'https://', 'www.')):
                    url = word
                    break
            
            if url:
                # Stream SEO analysis events
                async for event in seo_analysis_stream(url, session_id):
                    yield event
            else:
                yield create_ag_ui_event("error", {"message": "No valid URL found in message"})
        else:
            # Handle general chat
            yield create_ag_ui_event("message", {
                "content": "Hello! I'm your SEO analysis assistant. Please provide a website URL to analyze for SEO optimization opportunities.",
                "type": "assistant"
            })
            
    except Exception as e:
        logger.error(f"Chat stream error: {e}")
        yield create_ag_ui_event("error", {"message": str(e)})

async def seo_analysis_stream(url: str, session_id: str) -> AsyncGenerator[str, None]:
    """Stream SEO analysis progress events"""
    try:
        # Start analysis event
        yield create_ag_ui_event("analysis_start", {
            "url": url,
            "message": f"Starting SEO analysis for {url}..."
        })
        
        # Simulate progress events (in real implementation, these would come from CrewAI)
        progress_steps = [
            {"step": "extraction", "message": "Extracting website data..."},
            {"step": "content_analysis", "message": "Analyzing content strategy..."},
            {"step": "technical_analysis", "message": "Performing technical SEO analysis..."},
            {"step": "report_generation", "message": "Generating comprehensive report..."}
        ]
        
        for i, step in enumerate(progress_steps):
            await asyncio.sleep(1)  # Simulate processing time
            yield create_ag_ui_event("analysis_progress", {
                "step": step["step"],
                "message": step["message"],
                "progress": (i + 1) / len(progress_steps) * 100
            })
        
        # Run actual analysis
        if seo_system:
            result = seo_system.analyze_website(url)
            
            if result["status"] == "success":
                yield create_ag_ui_event("analysis_complete", {
                    "url": url,
                    "message": "SEO analysis completed successfully!",
                    "report_file": result.get("report_file"),
                    "timestamp": result["timestamp"]
                })
                
                # Try to read and send report content
                try:
                    with open("seo_analysis_report.md", "r") as f:
                        report_content = f.read()
                    yield create_ag_ui_event("report", {
                        "content": report_content,
                        "format": "markdown"
                    })
                except FileNotFoundError:
                    yield create_ag_ui_event("message", {
                        "content": "Analysis completed but report file not found.",
                        "type": "warning"
                    })
            else:
                yield create_ag_ui_event("analysis_error", {
                    "url": url,
                    "error": result.get("error", "Unknown error"),
                    "message": "SEO analysis failed. Please try again."
                })
        else:
            yield create_ag_ui_event("error", {"message": "SEO system not available"})
            
    except Exception as e:
        logger.error(f"SEO analysis stream error: {e}")
        yield create_ag_ui_event("error", {"message": str(e)})

def create_ag_ui_event(event_type: str, data: Dict[str, Any]) -> str:
    """Create an AG-UI compatible event"""
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    return f"data: {json.dumps(event)}\n\n"

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "CrewAI SEO Analysis API",
        "version": "1.0.0",
        "description": "AG-UI compatible API for SEO analysis using CrewAI",
        "endpoints": {
            "/health": "Health check",
            "/analyze": "Direct SEO analysis",
            "/chat": "AG-UI compatible chat interface"
        }
    }

if __name__ == "__main__":
    print("Starting CrewAI SEO Analysis Server...")
    print("Server will be available at: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "ag_ui_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

