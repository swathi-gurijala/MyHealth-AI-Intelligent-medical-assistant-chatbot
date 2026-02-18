from datetime import datetime

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .ai_models import get_medical_query_engine
from .models import (
    ChatResponse,
    MedicalQueryRequest,
    MedicalQueryResponse,
    RecommendationRequest,
    RecommendationResponse,
    SymptomInput,
    UserHistory,
)
from .services import generate_recommendations, parse_medical_report, triage_message
from .storage import add_history, get_history, init_db

app = FastAPI(title="MyHealth AI Backend", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok", "service": "myhealth-ai-backend"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: SymptomInput) -> ChatResponse:
    response, conditions, urgency, specialist = triage_message(payload.message, payload.symptoms)
    add_history(
        payload.user_id,
        datetime.utcnow().isoformat(),
        "chat",
        f"message={payload.message}; conditions={conditions}; urgency={urgency}",
    )
    return ChatResponse(
        response=response,
        possible_conditions=conditions,
        urgency=urgency,
        specialist=specialist,
    )


@app.post("/api/ai-query", response_model=MedicalQueryResponse)
def ai_medical_query(payload: MedicalQueryRequest) -> MedicalQueryResponse:
    engine = get_medical_query_engine()
    answer = engine.answer(payload.query)
    add_history(
        payload.user_id,
        datetime.utcnow().isoformat(),
        "ai_query",
        f"query={payload.query}; ai_answer={answer[:180]}",
    )
    return MedicalQueryResponse(answer=answer)


@app.post("/api/analyze-report")
async def analyze_report(user_id: str, file: UploadFile = File(...)) -> dict:
    raw = await file.read()
    analysis = parse_medical_report(file.filename or "uploaded_report.txt", raw)
    add_history(
        user_id,
        datetime.utcnow().isoformat(),
        "report",
        f"file={file.filename}; alerts={analysis['alerts']}",
    )
    return analysis


@app.post("/api/recommendations", response_model=RecommendationResponse)
def recommendations(payload: RecommendationRequest) -> RecommendationResponse:
    recs = generate_recommendations(payload.conditions)
    add_history(
        payload.user_id,
        datetime.utcnow().isoformat(),
        "recommendation",
        f"conditions={payload.conditions}",
    )
    return RecommendationResponse(**recs)


@app.get("/api/history/{user_id}", response_model=UserHistory)
def history(user_id: str) -> UserHistory:
    entries = get_history(user_id)
    return UserHistory(user_id=user_id, entries=entries)
