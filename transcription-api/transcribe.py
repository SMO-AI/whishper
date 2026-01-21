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
    
    # We save to a temp file to allow Pyannote (and Faster Whisper) to access the file directly.
    # This is also more memory efficient than holding the numpy array in memory.
    temp_filename = f"temp_{int(time.time())}_{uuid.uuid4().hex}.audio"
    try:
        with open(temp_filename, 'wb') as f:
            f.write(contents)
        
        return await transcribe_audio(temp_filename, model_size, language, device, task, diarize, num_speakers)
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

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
        
        # Apply Pyannote Diarization if requested and not using Groq (Groq handles it differently or upstream)
        # We only run this if audio is a string (filepath), which it should be now.
        if diarize and isinstance(audio, str) and not model_size.startswith("groq:"):
            print("Running Pyannote Diarization...")
            try:
                from processors.diarizer import PyannoteDiarizer
                diarizer = PyannoteDiarizer()
                # Run diarization
                diarization_result = diarizer.run_diarization(audio, num_speakers=num_speakers)
                # Align speakers with segments
                result["segments"] = diarizer.assign_speakers_to_segments(result["segments"], diarization_result)
                print("Pyannote Diarization completed.")
            except Exception as e:
                print(f"Pyannote Diarization failed: {e}")
                
        return result

    import asyncio
    return await asyncio.to_thread(run_inference)
