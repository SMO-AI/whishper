import os
import time
import logging
import io
import math
import uuid
import soundfile as sf
import numpy as np
from typing import Union, Optional
from groq import Groq, RateLimitError, InternalServerError, APIConnectionError
from .backend import Backend, Transcription, Segment, WordData
from processors.diarizer import LlamaDiarizer

logger = logging.getLogger(__name__)

class GroqBackend(Backend):
    name: str = "groq"
    
    def __init__(self, model_size: str, device: str = "cpu"):
        self.model_size = model_size
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def supported_model_sizes(self) -> list[str]:
        return ["distil-whisper-large-v3-en", "whisper-large-v3", "whisper-large-v3-turbo"]

    def get_model(self) -> None:
        pass

    def load(self) -> None:
        pass

    def transcribe(self, input_data: Union[np.ndarray, str], 
                  silent: bool = False, 
                  language: Optional[str] = None, 
                  task: str = "transcribe",
                  diarize: bool = False,
                  num_speakers: Optional[int] = None) -> Transcription:
        """
        Transcribes audio using Groq API with robust retry logic and word-level timestamps.
        """
        
        # Determine source: if string, it's a path; if ndarray, we need to buffer it.
        if isinstance(input_data, str):
            audio_file = open(input_data, "rb")
        else:
            buffer = io.BytesIO()
            # Standard Whisper sample rate is 16kHz
            sf.write(buffer, input_data, 16000, format='WAV', subtype='PCM_16')
            buffer.name = "audio.wav"
            buffer.seek(0)
            audio_file = buffer

        params = {
            "file": audio_file,
            "model": self.model_size,
            "response_format": "verbose_json",
            "timestamp_granularities": ["word", "segment"],
        }
        
        if language and language != "auto" and task == "transcribe":
            params["language"] = language

        # Robust Retry mechanism with exponential backoff (CTO-level reliability)
        max_retries = 5
        backoff_factor = 2
        
        for attempt in range(max_retries):
            try:
                if task == "translate":
                    completion = self.client.audio.translations.create(**params)
                else:
                    completion = self.client.audio.transcriptions.create(**params)
                break # Success!
            except (RateLimitError, InternalServerError, APIConnectionError) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Groq API failed after {max_retries} attempts: {e}")
                    raise
                
                wait_time = backoff_factor ** attempt
                logger.warning(f"Groq API error (attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                audio_file.seek(0) # Reset file pointer for retry
            finally:
                # If we opened a file from path, we don't close it yet as we might retry.
                # But it will be closed at the end of function.
                pass

        if isinstance(input_data, str):
            audio_file.close()

        # Map Groq/OpenAI-compatible response to our internal Transcription format
        segments: list[Segment] = []
        
        # Get segments from completion. 
        # completion is typically a VerboseJsonResponse object
        raw_segments = getattr(completion, 'segments', [])
        
        for seg in raw_segments:
            seg_dict = seg if isinstance(seg, dict) else seg.__dict__
            
            words_data: list[WordData] = []
            # Check if word-level timestamps were returned
            if 'words' in seg_dict and seg_dict['words']:
                for w in seg_dict['words']:
                    w_dict = w if isinstance(w, dict) else w.__dict__
                    words_data.append({
                        "word": w_dict.get('word', ''),
                        "start": w_dict.get('start', 0.0),
                        "end": w_dict.get('end', 0.0),
                        "score": 1.0 # Groq doesn't provide word-level scores usually
                    })
            
            segments.append({
                "id": uuid.uuid4().hex,
                "text": seg_dict.get('text', ''),
                "start": seg_dict.get('start', 0.0),
                "end": seg_dict.get('end', 0.0),
                "score": round(math.exp(seg_dict.get('avg_logprob', 0.0)), 2) if 'avg_logprob' in seg_dict else 0.0,
                "words": words_data
            })

        result = {
            "text": completion.text,
            "language": getattr(completion, 'language', language or 'unknown'),
            "duration": completion.duration,
            "segments": segments,
            "processing_duration": 0.0 # Will be set by caller
        }

        if diarize:
            import asyncio
            diarizer = LlamaDiarizer(api_key=os.environ.get("GROQ_API_KEY"))
            # We are running inside a thread (run_inference), so we might need a separate loop or just run sync if possible.
            # But LlamaDiarizer.diarize is async. Let's make a small helper or run it in a new loop.
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result["segments"] = loop.run_until_complete(diarizer.diarize(result["segments"], num_speakers))
                loop.close()
            except Exception as e:
                logger.error(f"Diarization failed: {e}")

        return result
