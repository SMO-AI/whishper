
import sys
from unittest.mock import MagicMock

# Mock groq and torch module before importing diarizer
sys.modules["groq"] = MagicMock()
sys.modules["torch"] = MagicMock()

import unittest
from processors.diarizer import PyannoteDiarizer

# Mock classes to simulate Pyannote output
class MockTurn:
    def __init__(self, start, end):
        self.start = start
        self.end = end

class MockDiarization:
    def __init__(self, turns):
        self.turns = turns
    
    def itertracks(self, yield_label=True):
        for start, end, speaker in self.turns:
            yield MockTurn(start, end), None, speaker

class TestPyannoteAlignment(unittest.TestCase):
    def test_alignment(self):
        diarizer = PyannoteDiarizer(auth_token="dummy")
        
        # Mock diarization: 
        # Speaker A: 0.0 - 5.0
        # Speaker B: 5.0 - 10.0
        mock_diarization = MockDiarization([
            (0.0, 5.0, "SPEAKER_A"),
            (5.0, 10.0, "SPEAKER_B")
        ])
        
        # Mock Whisper segments
        segments = [
            {
                "start": 0.0, "end": 4.0, "text": "Hello world",
                "words": [
                    {"start": 0.0, "end": 1.0, "word": "Hello"},
                    {"start": 1.0, "end": 2.0, "word": "world"} # purely in A
                ]
            },
            {
                "start": 4.5, "end": 6.0, "text": "Transition here",
                "words": [
                    {"start": 4.5, "end": 4.9, "word": "Transition"}, # mostly in A
                    {"start": 5.1, "end": 6.0, "word": "here"}        # purely in B
                ]
            },
             {
                "start": 6.0, "end": 8.0, "text": "I am B",
                "words": [
                    {"start": 6.0, "end": 7.0, "word": "I"},
                    {"start": 7.0, "end": 8.0, "word": "am"}
                ]
            }
        ]
        
        updated_segments = diarizer.assign_speakers_to_segments(segments, mock_diarization)
        
        # Checks
        self.assertEqual(updated_segments[0]["speaker"], "SPEAKER_A")
        
        # The second segment is tricky. 
        # "Transition" (4.5-4.9, dur=0.4) -> A
        # "here" (5.1-6.0, dur=0.9) -> B
        # Dominant should be B
        self.assertEqual(updated_segments[1]["speaker"], "SPEAKER_B")
        
        self.assertEqual(updated_segments[2]["speaker"], "SPEAKER_B")
        
        print("Test passed!")

if __name__ == '__main__':
    unittest.main()
