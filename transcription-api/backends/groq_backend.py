import os
from .backend import Backend, Transcription, Segment
from groq import Groq
import soundfile as sf
import io
import math

class GroqBackend(Backend):
    name: str = "groq"
    
    def __init__(self, model_size, device: str = "cpu"):
        self.model_size = model_size
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def supported_model_sizes(self) -> list[str]:
        return ["distil-whisper-large-v3-en", "whisper-large-v3", "whisper-large-v3-turbo"]

    def get_model(self) -> None:
        # No download needed for API
        pass

    def load(self) -> None:
        # No load needed for API
        pass

    def transcribe(self, input, silent: bool = False, language: str = None) -> Transcription:
        # input is typically np.ndarray from transcribe.py
        # We need to convert it to a file-like object for Groq API
        
        buffer = io.BytesIO()
        # Assuming input is the audio array and sample rate is 16000 (standard for Whisper)
        # Faster-whisper decode_audio returns float32, usually normalized -1 to 1
        sf.write(buffer, input, 16000, format='WAV', subtype='PCM_16')
        buffer.name = "audio.wav"
        buffer.seek(0)

        params = {
            "file": buffer,
            "model": self.model_size,
            "response_format": "verbose_json",
        }
        
        if language and language != "auto":
            params["language"] = language

        completion = self.client.audio.transcriptions.create(**params)

        # Map Groq response to Transcription format
        segments: list[Segment] = []
        
        for seg in completion.segments:
            # Groq might not return words for all models? 
            # If segments have no words, we handle it.
            # verbose_json usually returns segments.
            
            # Create a unique ID for the segment
            import uuid
            id = uuid.uuid4().hex
            
            # Words logic
            words_list = []
            # Check if 'words' exists in the segment (it might not if not requested or supported)
            # Groq implementation of 'verbose_json' usually follows OpenAI which has 'words' if timestamp_granularities=['word']
            # But currently we didn't pass timestamp_granularities.
            # Add it if we want words? existing backend produces words.
            # Whisper API defaults often don't include words unless requested.
            
            segment_extract: Segment = {
                "id": id,
                "text": seg.get('text', ''),
                "start": seg.get('start', 0.0),
                "end": seg.get('end', 0.0),
                "score": 0.0, # Groq response might not have 'avg_logprob' easily accessible in pydantic model or dict?
                # seg is usually a dict or object. create returns an object.
                "words": [] 
            }
            
            # Handle score if available
            if hasattr(seg, 'avg_logprob'):
                 segment_extract["score"] = round(math.exp(seg.avg_logprob), 2)
            elif isinstance(seg, dict) and 'avg_logprob' in seg:
                 segment_extract["score"] = round(math.exp(seg['avg_logprob']), 2)

            segments.append(segment_extract)

        transcription: Transcription = {
            "text": completion.text,
            "language": completion.language,
            "duration": completion.duration,
            "segments": segments,
        }
        
        return transcription
