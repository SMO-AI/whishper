from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Depends
from models import ModelSize, Languages, DeviceType
from transcribe import transcribe_file, transcribe_from_filename
import uvicorn
import os
import time
from enum import Enum
from typing import Annotated, Optional, Dict, Union
from backends.fasterwhisper import FasterWhisperBackend
from supabase import create_client, Client
from pydantic import BaseModel
import asyncio
import boto3
from botocore.exceptions import NoCredentialsError

app = FastAPI()

# Initialize Supabase Client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

# Initialize S3 Client
s3_client = boto3.client(
    's3',
    endpoint_url=os.environ.get("S3_ENDPOINT"),
    aws_access_key_id=os.environ.get("S3_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("S3_REGION")
)
BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

class UserContext(BaseModel):
    user: object
    token: str

async def upload_to_s3(file_path: str, object_name: str) -> Optional[str]:
    try:
        s3_client.upload_file(file_path, BUCKET_NAME, object_name)
        endpoint = os.environ.get("S3_ENDPOINT", "")
        if "backblaze" in endpoint:
             return f"{endpoint}/{BUCKET_NAME}/{object_name}"
        return object_name
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None

async def get_current_user(authorization: Annotated[Optional[str], Header()] = None) -> Optional[UserContext]:
    if not authorization:
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        return UserContext(user=user.user, token=token)
    except Exception as e:
        print(f"Auth Error: {e}")
        return None

@app.post("/diarize/")
async def diarize_endpoint(
    data: Dict,
    ctx: Annotated[Optional[UserContext], Depends(get_current_user)] = None
):
    segments = data.get("segments", [])
    num_speakers = data.get("num_speakers")
    
    if not segments:
        return {"segments": []}
    
    from processors.diarizer import LlamaDiarizer
    diarizer = LlamaDiarizer(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Run diarization
    try:
        updated_segments = await diarizer.diarize(segments, num_speakers)
        return {"segments": updated_segments}
    except Exception as e:
        print(f"Diarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/")
async def transcribe_endpoint(
    ctx: Annotated[Optional[UserContext], Depends(get_current_user)] = None,
    file: UploadFile = File(None),
    filename: str = None,
    model_size: ModelSize = ModelSize.small, 
    language: Languages = Languages.auto,
    device: str = "cpu",
    task: str = "transcribe",
    diarize: bool = False,
    num_speakers: Optional[int] = None
):
    user = ctx.user if ctx else None
    token = ctx.token if ctx else None
    user_id = user.id if user else "internal_service"

    if device != "cpu" and device != "cuda":
        return {"detail": "Device must be either cpu or cuda"}
    
    print(f"Transcribing with model {model_size.value} on device {device} and task {task} for user {user_id}...")
    
    if file is not None:
        # Save UploadFile to disk temporarily to upload to S3 later
        # Use a generic prefix if user is missing
        prefix = user_id
        saved_filename = f"{prefix}_{int(time.time())}_{file.filename}"
        file_path = os.path.join(os.environ.get("UPLOAD_DIR", "/tmp"), saved_filename)
        with open(file_path, "wb") as buffer:
            # Read from UploadFile (which is Spooled)
            content = await file.read() 
            buffer.write(content)
            
        print(f"File saved to {file_path}")
        
        # Use transcribe_from_filename to reuse the saved file and preserve extension/path for Groq/Pyannote
        result = await transcribe_from_filename(saved_filename, model_size.value, language.value, device, task, diarize, num_speakers)
    elif filename is not None:
        saved_filename = filename
        result = await transcribe_from_filename(filename, model_size.value, language.value, device, task, diarize, num_speakers)
    else:
        return {"detail": "No file uploaded"}

    # Upload to S3 (Only if S3 is configured and file exists)
    s3_url = None
    if saved_filename:
        upload_dir = os.environ.get("UPLOAD_DIR", "/tmp")
        full_path = os.path.join(upload_dir, saved_filename)
        # Check if file exists before trying to upload
        if os.path.exists(full_path) and os.environ.get("S3_BUCKET_NAME"):
             s3_url = await upload_to_s3(full_path, saved_filename)
             # os.remove(full_path) 
    
    # Log usage & Save Transcription (Only if we have a valid user)
    if user and token:
        try:
            # Pricing logic for different models
            # Rates per hour in USD
            rates = {
                "distil-whisper-large-v3-en": 0.02,
                "whisper-large-v3": 0.111,
                "whisper-large-v3-turbo": 0.04,
                "tiny": 0.01, # Placeholder for local models
                "base": 0.02,
                "small": 0.03,
                "medium": 0.06,
                "large": 0.09
            }
            rate = rates.get(model_size.value, 0.03) # Default to 0.03 if unknown
            duration = result.get("duration", 0.0)
            cost = (duration / 3600.0) * rate
            
            user_client = create_client(url, key)
            user_client.postgrest.auth(token)
            
            # 1. Log Usage
            usage_data = {
                "user_id": user.id,
                "usage_type": "transcription_seconds",
                "amount": float(duration),
                "cost": float(cost),
                "details": {
                    "model": model_size.value,
                    "rate_per_hr": rate
                }
            }
            user_client.table("whishper_usage_logs").insert(usage_data).execute()
            
            # 2. Save Transcription
            transcription_data = {
                "user_id": user.id,
                "filename": saved_filename,
                "s3_url": s3_url,
                "text": result.get("text", ""),
                "language": result.get("language", language.value),
                "duration": float(duration),
                "model": model_size.value,
                "mimetype": file.content_type if file else None,
                "file_size": os.path.getsize(full_path) if os.path.exists(full_path) else None
            }
            user_client.table("whishper_transcriptions").insert(transcription_data).execute()
            
        except Exception as e:
            print(f"DB Error: {e}")
    else:
        print("Skipping Supabase logging - no authenticated user context")

    return result

@app.get("/healthcheck/")
async def healthcheck():
    return {"status": "healthy"}

if __name__ == "__main__":
    # Get model list (comma separated) from environment variable
    model_list = os.environ.get("WHISPER_MODELS", "tiny,base,small")
    model_list = model_list.split(",")
    for model in model_list:
        if model.startswith("groq:"):
            continue
        m = FasterWhisperBackend(model_size=model)
        m.get_model()
    uvicorn.run(app, host="0.0.0.0", port=8000)