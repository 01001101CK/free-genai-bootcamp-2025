from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import traceback
from .get_transcript import YouTubeTranscriptDownloader
from .rag import TranscriptRAG
from .config import get_supabase_client

app = FastAPI()

# Initialize clients
supabase_client = get_supabase_client()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Backend is running"}

@app.get("/test")
async def test():
    return {"status": "ok"}

class VideoRequest(BaseModel):
    videoUrl: str

@app.post("/process-video")
async def process_video(request: VideoRequest) -> Dict[str, Any]:
    try:
        print(f"Received video URL: {request.videoUrl}")
        return {"message": "Received URL", "url": request.videoUrl}
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 