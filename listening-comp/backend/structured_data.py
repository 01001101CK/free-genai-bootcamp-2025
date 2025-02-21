from pydantic import BaseModel
from typing import List, Optional

class Question(BaseModel):
    text: str
    options: List[str]
    correct_answer: str
    difficulty: str
    transcript_timestamp: float

class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float
    speaker: Optional[str]

class ListeningExercise(BaseModel):
    video_id: str
    title: str
    questions: List[Question]
    transcript: List[TranscriptSegment]
