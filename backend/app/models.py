from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SymptomInput(BaseModel):
    user_id: str
    symptoms: List[str] = Field(default_factory=list)
    message: str


class ChatResponse(BaseModel):
    response: str
    possible_conditions: List[str]
    urgency: str
    specialist: Optional[str] = None


class RecommendationRequest(BaseModel):
    user_id: str
    conditions: List[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    diet: List[str]
    lifestyle: List[str]
    exercises: List[str]
    home_remedies: List[str]
    otc_medicines: List[str]


class MedicalQueryRequest(BaseModel):
    user_id: str
    query: str


class MedicalQueryResponse(BaseModel):
    answer: str


class HistoryEntry(BaseModel):
    timestamp: datetime
    interaction_type: str
    summary: str


class UserHistory(BaseModel):
    user_id: str
    entries: List[HistoryEntry]
