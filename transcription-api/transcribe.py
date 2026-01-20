from backends.fasterwhisper import FasterWhisperBackend
from backends.groq_backend import GroqBackend
from backends.backend import Transcription
from faster_whisper import decode_audio
from models import DeviceType
from typing import Optional
import numpy as np
import io
import os
import time

def convert_audio(file) -> np.ndarray:
        return decode_audio(file, split_stereo=False, sampling_rate=16000)

async def transcribe_from_filename(filename: str,
                                    model_size: str,
                                    language: Optional[str] = None,
                                    device: DeviceType = DeviceType.cpu,
                                    task: str = "transcribe",
                                    diarize: bool = False,
                                    num_speakers: Optional[int] = None) -> Transcription:
    
    filepath = os.path.join(os.environ["UPLOAD_DIR"], filename)
    if not os.path.exists(filepath):
        raise RuntimeError(f"file not found in {filepath}")
    
    # Optimization: For Groq API, pass the file path directly to avoid expensive decoding to np.ndarray
    if model_size.startswith("groq:"):
        return await transcribe_audio(filepath, model_size, language, device, task, diarize, num_speakers)
        
    audio = convert_audio(filepath)
    return await transcribe_audio(audio, model_size, language, device, task, diarize, num_speakers)

async def transcribe_file(file: io.BytesIO, 
                          model_size: str, 
                          language: Optional[str] = None, 
                          device: DeviceType = DeviceType.cpu,
                          task: str = "transcribe",
                          diarize: bool = False,
                          num_speakers: Optional[int] = None) -> Transcription:
    contents = await file.read()  # async read
    
    # Optimization: For Groq API, just pass the raw bytes via BytesIO if it's small, 
    # but currently transcribe_audio expects ndarray or path. 
    # Let's stick to the current logic of saving/decoding for local models, 
    # but for Groq we could ideally pass BytesIO. 
    # However, chunking (handled in Go) ensures we handle large files as paths.

    if len(contents) < 150 * 1024 * 1024:  # file is smaller than 150MB
            audio = convert_audio(io.BytesIO(contents))
    else:
         # Save the uploaded file temporarily on disk
        temp_filename = f"temp_{int(time.time())}_{uuid.uuid4().hex}.audio"
        with open(temp_filename, 'wb') as f:
            f.write(contents)
        
        if model_size.startswith("groq:"):
             res = await transcribe_audio(temp_filename, model_size, language, device, task, diarize, num_speakers)
             os.remove(temp_filename)
             return res

        audio = convert_audio(temp_filename)
        os.remove(temp_filename)
    return await transcribe_audio(audio, model_size, language, device, task, diarize, num_speakers)

from typing import Union
import uuid

async def transcribe_audio(audio: Union[np.ndarray, str], 
                           model_size: str,
                           language: Optional[str] = None, 
                           device: DeviceType = DeviceType.cpu,
                           task : str = "transcribe",
                           diarize: bool = False,
                           num_speakers: Optional[int] = None) -> Transcription:
    
    if language == "auto":
        language = None

    def run_inference():
        # Load the model
        if model_size.startswith("groq:"):
            actual_model = model_size.split(":", 1)[1]
            model = GroqBackend(model_size=actual_model, device=device)
        else:
            model = FasterWhisperBackend(model_size=model_size, device=device)
        
        model.get_model()
        model.load()
        # Transcribe the data (might be ndarray or filepath)
        start_time = time.time()
        result = model.transcribe(audio, silent=True, language=language, task=task, diarize=diarize, num_speakers=num_speakers)
        end_time = time.time()
        result["processing_duration"] = end_time - start_time
        return result

    import asyncio
    return await asyncio.to_thread(run_inference)
