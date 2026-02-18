# MyHealth AI: Intelligent Health Companion & Diagnostic Assistant

MyHealth AI is a full-stack healthcare chatbot platform built to support **SDG Goal 3: Good Health and Well-being**.
It provides:

- AI-style symptom triage chat
- ClinicalBERT-powered retrieval for medical question understanding
- Generative AI responses for user medical queries
- Medical report scan and alert extraction
- Personalized health recommendations
- Emergency risk detection and specialist guidance
- User history tracking for follow-up

> ⚠️ This project is for educational and decision-support use only, not a replacement for licensed medical professionals.

## Tech Stack

### Frontend
- React + Vite
- Plain CSS UI with modular components
- REST API integration with backend

### Backend
- FastAPI
- Pydantic models
- SQLite for interaction history
- ClinicalBERT embeddings (`emilyalsentzer/Bio_ClinicalBERT`) for context retrieval
- Text2Text generation (`google/flan-t5-small`) for AI medical query responses
- Rule-based triage/recommendation fallback (always available if models fail to load)

---

## Project Structure

```
MyHealth-AI-Intelligent-medical-assistant-chatbot/
├── backend/
│   ├── app/
│   │   ├── ai_models.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── services.py
│   │   └── storage.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/SectionCard.jsx
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Backend runs at: `http://localhost:8000`

### API Endpoints
- `GET /api/health` — service check
- `POST /api/chat` — symptom triage and urgency detection
- `POST /api/ai-query` — ClinicalBERT + generator based AI answer to medical queries
- `POST /api/analyze-report?user_id=<id>` — report parsing and alerts
- `POST /api/recommendations` — personalized guidance
- `GET /api/history/{user_id}` — interaction history

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

Set a custom backend URL (optional):

```bash
echo "VITE_API_URL=http://localhost:8000" > .env
```

---

## Running in GitHub Codespaces

Run backend in one terminal:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Run frontend in second terminal:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Codespaces will prompt to expose ports `8000` and `5173`.

---

## Push This Code to GitHub

Use these commands from repository root:

```bash
git add .
git commit -m "Add ClinicalBERT medical query pipeline and frontend AI query UI"
git push origin <your-branch-name>
```

If starting a new branch:

```bash
git checkout -b feature/clinicalbert-ai-query
git push -u origin feature/clinicalbert-ai-query
```

---

## End-to-End Flow

1. User enters symptoms and message in chat section.
2. Frontend calls `/api/chat`.
3. Backend triages symptoms, flags urgency, suggests specialist, stores interaction.
4. User asks a free-form medical query.
5. Frontend calls `/api/ai-query`.
6. Backend retrieves medical context via ClinicalBERT embeddings and produces a safe AI answer.
7. Frontend requests `/api/recommendations` using predicted conditions.
8. User uploads report (`txt/csv/pdf`).
9. Backend extracts key markers and returns alerts.
10. User can fetch full history via `/api/history/{user_id}`.

---

## Future AI/ML Enhancements

- Replace rule-based triage with fully fine-tuned ClinicalBERT/BioBERT classifiers
- Use larger medically tuned LLMs with strict safety post-processing
- Add vector DB + RAG for grounded, cited medical Q&A
- Add authentication and encrypted health records
- Integrate doctor directory and appointment booking

---

## License

This project follows the repository `LICENSE`.
