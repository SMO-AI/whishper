from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Depends
from models import ModelSize, Languages, DeviceType
from transcribe import transcribe_file, transcribe_from_filename
import uvicorn
import os
import time
from enum import Enum
from typing import Annotated, Optional
from backends.fasterwhisper import FasterWhisperBackend
from supabase import create_client, Client
from pydantic import BaseModel
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

async def upload_to_s3(file_path: str, object_name: str) -> str | None:
    try:
        s3_client.upload_file(file_path, BUCKET_NAME, object_name)
        endpoint = os.environ.get("S3_ENDPOINT", "")
        if "backblaze" in endpoint:
             return f"{endpoint}/{BUCKET_NAME}/{object_name}"
        return object_name
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None

async def get_current_user(authorization: Annotated[str | None, Header()] = None) -> UserContext:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        return UserContext(user=user.user, token=token)
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid Token")

@app.post("/transcribe/")
async def transcribe_endpoint(
    ctx: Annotated[UserContext, Depends(get_current_user)],
    file: UploadFile = File(None),
    filename: str = None,
    model_size: ModelSize = ModelSize.small, 
    language: Languages = Languages.auto,
    device: str = "cpu",
    task: str = "transcribe"
):
    user = ctx.user
    token = ctx.token

    if device != "cpu" and device != "cuda":
        return {"detail": "Device must be either cpu or cuda"}
    
    print(f"Transcribing with model {model_size.value} on device {device} and task {task} for user {user.id}...")
    
    result = None
    saved_filename = filename
    
    # Save UploadFile to disk temporarily to upload to S3 later
    if file is not None:
        saved_filename = f"{user.id}_{int(time.time())}_{file.filename}"
        file_path = os.path.join(os.environ.get("UPLOAD_DIR", "/tmp"), saved_filename)
        with open(file_path, "wb") as buffer:
            # Read from UploadFile (which is Spooled)
            content = await file.read() 
            buffer.write(content)
            # Reset file cursor for transcription
            await file.seek(0) 
            
        result = await transcribe_file(file, model_size.value, language.value, device, task)
    elif filename is not None:
        saved_filename = filename
        result = await transcribe_from_filename(filename, model_size.value, language.value, device, task)
    else:
        return {"detail": "No file uploaded"}

    # Upload to S3
    s3_url = None
    if saved_filename:
        upload_dir = os.environ.get("UPLOAD_DIR", "/tmp")
        full_path = os.path.join(upload_dir, saved_filename)
        if os.path.exists(full_path):
             s3_url = await upload_to_s3(full_path, saved_filename)
             # os.remove(full_path) 
    
    # Log usage & Save Transcription
    try:
        duration = result.get("duration", 0.0)
        cost = (duration / 3600.0) * 0.03
        
        user_client = create_client(url, key)
        user_client.postgrest.auth(token)
        
        # 1. Log Usage
        usage_data = {
            "user_id": user.id,
            "usage_type": "transcription_seconds",
            "amount": float(duration),
            "cost": float(cost),
            "details": {"model": model_size.value}
        }
        user_client.table("usage_logs").insert(usage_data).execute()
        
        # 2. Save Transcription
        transcription_data = {
            "user_id": user.id,
            "filename": saved_filename,
            "s3_url": s3_url,
            "text": result.get("text", ""),
            "language": result.get("language", language.value),
            "duration": float(duration),
            "model": model_size.value
        }
        user_client.table("transcriptions").insert(transcription_data).execute()
        
    except Exception as e:
        print(f"DB Error: {e}")

    return result

@app.get("/healthcheck/")
async def healthcheck():
    return {"status": "healthy"}

if __name__ == "__main__":
    load_dotenv()

    # Get model list (comma separated) from environment variable
    model_list = os.environ.get("WHISPER_MODELS", "tiny,base,small")
    model_list = model_list.split(",")
    for model in model_list:
        if model.startswith("groq:"):
            continue
        m = FasterWhisperBackend(model_size=model)
        m.get_model()
    uvicorn.run(app, host="0.0.0.0", port=8000)