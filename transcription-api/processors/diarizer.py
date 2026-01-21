
import os
import json
import logging
import asyncio
from typing import List, Dict, Optional
from groq import Groq
import torch

try:
    from pyannote.audio import Pipeline
except ImportError:
    Pipeline = None

logger = logging.getLogger(__name__)

class LlamaDiarizer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.error("GROQ_API_KEY missing for LlamaDiarizer")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
        self.semaphore = asyncio.Semaphore(3) # Limit parallel requests to 3

    async def _process_batch(self, batch: List[Dict], context: List[Dict], speaker_hint: str) -> Dict:
        """
        Processes a single batch of segments with context and robust error handling.
        """
        system_prompt = (
            "You are an expert in conversation analysis. Your task is to perform speaker diarization and role assignment.\n"
            f"{speaker_hint}\n"
            "1. Identify different speakers (e.g., Speaker 1, Speaker 2).\n"
            "2. Detect roles based on context (e.g., Doctor, Patient, Support, Interviewer).\n"
            "3. IMPORTANT: Maintain continuity. The 'context' segments already have assigned speakers.\n"
            "4. Your output must align with the context speaker identities. If you believe a new person is speaking, increment the speaker ID.\n\n"
            "Input: JSON object with 'context' (previously labeled) and 'current' (to be labeled).\n"
            "Output: JSON object where keys are IDs from 'current' and values are objects with 'speaker' and 'role'.\n"
            "Example: { \"seg_123\": { \"speaker\": \"Speaker 1\", \"role\": \"Doctor\" } }\n"
            "ONLY return the JSON object."
        )

        async with self.semaphore:
            try:
                prompt_content = {"context": context, "current": batch}
                
                # Set a reasonable timeout for the LLM response
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": json.dumps(prompt_content)}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.1
                    ),
                    timeout=20.0 # 20 seconds max per batch
                )
                
                content = response.choices[0].message.content
                
                # Robust parsing: handle cases where LLM might include markdown or extra text
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback to simple regex extract if JSON fails
                    import re
                    match = re.search(r"(\{.*\})", content, re.DOTALL)
                    if match:
                        return json.loads(match.group(1))
                    raise
            except Exception as e:
                logger.error(f"Error in LlamaDiarizer batch processing: {e}")
                return {s["id"]: {"speaker": "Speaker ?", "role": "Unknown"} for s in batch}

    async def diarize(self, segments: List[Dict], num_speakers: Optional[int] = None) -> List[Dict]:
        """
        Assigns speakers and roles using parallel processing and speaker pinning.
        """
        if not segments:
            return segments

        # Prepare concise version
        segments_to_process = [{"id": s["id"], "text": s["text"]} for s in segments]
        
        BATCH_SIZE = 30
        OVERLAP = 7 # Larger overlap for better pinning
        
        i = 0
        speaker_hint = f"Expected number of speakers: {num_speakers}." if num_speakers else ""
        
        while i < len(segments_to_process):
            start = i
            end = min(i + BATCH_SIZE, len(segments_to_process))
            
            # For each batch, we include the overlap as 'context' (now with previously assigned labels)
            context_start = max(0, start - OVERLAP)
            context = segments_to_process[context_start:start]
            
            batch = segments_to_process[start:end]
            
            # Record batch results
            batch_result = await self._process_batch(batch, context, speaker_hint)
            
            # Update segments_to_process with labels for pinning in next batch
            for idx in range(start, end):
                seg_id = segments_to_process[idx]["id"]
                # Convert back to string as JSON keys are strings
                seg_key = str(seg_id)
                if seg_key in batch_result:
                    res = batch_result[seg_key]
                    segments_to_process[idx]["speaker"] = res.get("speaker", "Speaker ?")
                    segments_to_process[idx]["role"] = res.get("role", "Unknown")
                else:
                    # Fallback if key missing
                    segments_to_process[idx]["speaker"] = "Speaker ?"
                    segments_to_process[idx]["role"] = "Unknown"
            
            i += BATCH_SIZE

        # Combine results back to original segments
        for i, seg in enumerate(segments):
            seg["speaker"] = segments_to_process[i].get("speaker", "Speaker ?")
            seg["role"] = segments_to_process[i].get("role", "Unknown")
        
        return segments


class PyannoteDiarizer:
    def __init__(self, auth_token: str = None):
        self.auth_token = auth_token or os.environ.get("HF_TOKEN")
        if not self.auth_token:
            logger.error("HF_TOKEN missing for PyannoteDiarizer")
        
        self.pipeline = None
        if Pipeline:
            try:                
                # Use CUDA if available
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                
                self.pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=self.auth_token
                )
                if self.pipeline:
                    self.pipeline.to(device)
            except Exception as e:
                logger.error(f"Failed to initialize Pyannote pipeline: {e}")

    def run_diarization(self, audio_path: str, num_speakers: Optional[int] = None):
        if not self.pipeline:
            raise RuntimeError("Pyannote pipeline not initialized")
        
        try:
            diarization = self.pipeline(audio_path, num_speakers=num_speakers)
            return diarization
        except Exception as e:
            logger.error(f"Pyannote inference error: {e}")
            raise

    def assign_speakers_to_segments(self, segments: List[Dict], diarization) -> List[Dict]:
        """
        Aligns Pyannote speaker turns with Whisper segments.
        Iterates through words in segments to find the most overlapping speaker.
        """
        # Convert diarization to list of turns for faster lookup
        # turn: (start, end, speaker)
        turns = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            turns.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
            
        # Helper to find speaker for a time range
        def find_speaker(start, end):
            max_overlap = 0
            best_speaker = None
            
            seg_center = (start + end) / 2
            
            # Simple check: find turn containing center
            # For more precision, we could calculate exact overlap duration
            for turn in turns:
                # Check for overlap
                overlap_start = max(start, turn["start"])
                overlap_end = min(end, turn["end"])
                overlap_duration = max(0, overlap_end - overlap_start)
                
                if overlap_duration > max_overlap:
                    max_overlap = overlap_duration
                    best_speaker = turn["speaker"]
            
            return best_speaker

        # Assign speakers to each word, then consensus for segment
        for segment in segments:
            speaker_counts = {}
            total_duration = segment.get("end", 0) - segment.get("start", 0)
            
            # If we have word timestamps (which we should from Faster Whisper)
            if "words" in segment and segment["words"]:
                for word in segment["words"]:
                    spk = find_speaker(word["start"], word["end"])
                    if spk:
                        word["speaker"] = spk
                        speaker_counts[spk] = speaker_counts.get(spk, 0) + (word["end"] - word["start"])
            else:
                # Fallback to segment level
                spk = find_speaker(segment["start"], segment["end"])
                if spk:
                    speaker_counts[spk] = total_duration

            # Determine dominant speaker for the segment
            if speaker_counts:
                dominant_speaker = max(speaker_counts, key=speaker_counts.get)
                segment["speaker"] = dominant_speaker
            else:
                segment["speaker"] = "Unknown"  # Or keep existing/null
        
        return segments
