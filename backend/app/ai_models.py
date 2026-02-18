from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import List

from transformers import AutoModel, AutoTokenizer, pipeline

logger = logging.getLogger(__name__)

CLINICAL_BERT_MODEL = "emilyalsentzer/Bio_ClinicalBERT"
GEN_MODEL = "google/flan-t5-small"


@dataclass
class KnowledgeItem:
    topic: str
    text: str


KNOWLEDGE_BASE: List[KnowledgeItem] = [
    KnowledgeItem(
        topic="diabetes",
        text=(
            "Diabetes care includes blood sugar monitoring, low glycemic nutrition, regular physical "
            "activity, medication adherence, and periodic HbA1c tests under physician supervision."
        ),
    ),
    KnowledgeItem(
        topic="hypertension",
        text=(
            "Hypertension management focuses on low sodium diet, blood pressure tracking, stress "
            "reduction, exercise, sleep quality, and prescribed antihypertensive medication."
        ),
    ),
    KnowledgeItem(
        topic="cold and cough",
        text=(
            "Most mild cold and cough cases improve with hydration, rest, steam inhalation, and "
            "symptomatic over-the-counter medicines when safe for the patient profile."
        ),
    ),
    KnowledgeItem(
        topic="heart emergency",
        text=(
            "Warning signs like chest pain, shortness of breath, fainting, or severe sweating can "
            "indicate emergency cardiac issues and require immediate emergency care."
        ),
    ),
]


class ClinicalBertRetriever:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(CLINICAL_BERT_MODEL)
        self.model = AutoModel.from_pretrained(CLINICAL_BERT_MODEL)

    def embed(self, text: str) -> List[float]:
        tokens = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
        )
        outputs = self.model(**tokens)
        cls_embedding = outputs.last_hidden_state[:, 0, :].detach().cpu().numpy().flatten()
        return cls_embedding.tolist()

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        a_norm = sum(x * x for x in a) ** 0.5
        b_norm = sum(y * y for y in b) ** 0.5
        if a_norm == 0 or b_norm == 0:
            return 0.0
        return dot / (a_norm * b_norm)

    def retrieve_context(self, query: str) -> str:
        query_vector = self.embed(query)
        scored = []
        for item in KNOWLEDGE_BASE:
            item_vector = self.embed(item.text)
            score = self.cosine_similarity(query_vector, item_vector)
            scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_items = [entry.text for _, entry in scored[:2]]
        return "\n".join(top_items)


class MedicalQueryEngine:
    def __init__(self) -> None:
        self.retriever = ClinicalBertRetriever()
        self.generator = pipeline("text2text-generation", model=GEN_MODEL)

    def answer(self, query: str) -> str:
        context = self.retriever.retrieve_context(query)
        prompt = (
            "You are a safe medical assistant. Provide educational guidance, not diagnosis. "
            "Mention emergency care for red-flag symptoms.\n"
            f"Context: {context}\n"
            f"Question: {query}\n"
            "Answer briefly in simple language:"
        )
        generated = self.generator(prompt, max_new_tokens=180, do_sample=False)
        answer = generated[0]["generated_text"].strip()
        return (
            f"{answer}\n\n"
            "Safety Note: This response is informational only and not a substitute for professional "
            "medical diagnosis or treatment."
        )


class FallbackMedicalQueryEngine:
    def answer(self, query: str) -> str:
        normalized = query.lower()
        if any(term in normalized for term in ["chest pain", "faint", "breath", "stroke", "seizure"]):
            return (
                "Your symptoms may indicate an emergency. Seek immediate emergency care. "
                "For non-emergency concerns, consult a physician for examination.\n\n"
                "Safety Note: This response is informational only and not a substitute for professional "
                "medical diagnosis or treatment."
            )
        return (
            "For general health concerns, track symptoms, stay hydrated, maintain rest, and consult a "
            "licensed doctor for personalized evaluation.\n\n"
            "Safety Note: This response is informational only and not a substitute for professional "
            "medical diagnosis or treatment."
        )


@lru_cache(maxsize=1)
def get_medical_query_engine() -> MedicalQueryEngine | FallbackMedicalQueryEngine:
    try:
        logger.info("Loading ClinicalBERT + generation pipeline for medical query engine")
        return MedicalQueryEngine()
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to load ML pipelines; using fallback engine: %s", exc)
        return FallbackMedicalQueryEngine()
