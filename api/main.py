import os
import uuid
import json
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import redis

from workflows.celery_app import process_video_task
from workflows.style_config import StylePresets

app = FastAPI(title="Subtitle Ninja", description="Video Subtitle Processing API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure directories exist
UPLOAD_DIR = Path("uploads")
DOWNLOAD_DIR = Path("downloads")
UPLOAD_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Redis connection for job status
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis_client = redis.Redis.from_url(redis_url)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main upload page"""
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())

@app.post("/upload")
async def upload_video(file: UploadFile = File(...), style_preset: str = Form("instagram_classic")):
    """Upload video file and start processing with style selection"""

    # Debug: Log received parameters
    print(f"DEBUG API: Received file: {file.filename}")
    print(f"DEBUG API: Received style: {style_preset}")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Validate file type
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Generate unique job ID and filename
    job_id = str(uuid.uuid4())
    input_filename = f"{job_id}_{file.filename}"
    input_path = UPLOAD_DIR / input_filename

    # Save uploaded file
    try:
        async with aiofiles.open(input_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Initialize job status in Redis
    job_data = {
        "status": "queued",
        "progress": 0,
        "message": "Video uploaded, processing queued",
        "input_file": input_filename,
        "output_file": None,
        "error": None
    }
    redis_client.set(f"job:{job_id}", json.dumps(job_data), ex=3600)

    # Validate style preset
    if style_preset not in StylePresets.list_presets():
        style_preset = "instagram_classic"  # Default fallback

    # Start processing task with style
    try:
        process_video_task.delay(job_id, str(input_path), style_preset)
    except Exception as e:
        job_data["status"] = "failed"
        job_data["error"] = f"Failed to queue processing: {str(e)}"
        redis_client.set(f"job:{job_id}", json.dumps(job_data), ex=3600)

    return {"job_id": job_id, "message": "File uploaded successfully, processing started"}

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get processing status for a job"""
    try:
        job_data = redis_client.get(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        return json.loads(job_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid job data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving job status: {str(e)}")

@app.get("/download/{job_id}")
async def download_processed_video(job_id: str):
    """Download the processed video"""
    try:
        job_data = redis_client.get(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")

        job = json.loads(job_data)
        if job["status"] != "completed":
            raise HTTPException(status_code=400, detail="Job not completed yet")

        if not job["output_file"]:
            raise HTTPException(status_code=404, detail="Output file not found")

        output_path = DOWNLOAD_DIR / job["output_file"]
        if not output_path.exists():
            raise HTTPException(status_code=404, detail="Output file does not exist")

        return FileResponse(
            path=str(output_path),
            filename=job["output_file"],
            media_type='video/mp4'
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid job data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving job: {str(e)}")

@app.delete("/job/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up job files and status"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_status[job_id]

    # Remove input file
    if job["input_file"]:
        input_path = UPLOAD_DIR / job["input_file"]
        if input_path.exists():
            input_path.unlink()

    # Remove output file
    if job["output_file"]:
        output_path = DOWNLOAD_DIR / job["output_file"]
        if output_path.exists():
            output_path.unlink()

    # Remove job status
    del job_status[job_id]

    return {"message": "Job cleaned up successfully"}

@app.get("/styles")
async def get_available_styles():
    """Get available subtitle style presets"""
    return {
        "presets": StylePresets.list_presets(),
        "preset_info": StylePresets.get_preset_info()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "subtitle-ninja-api"}

