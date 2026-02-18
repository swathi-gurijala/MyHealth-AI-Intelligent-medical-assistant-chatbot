from __future__ import annotations

import csv
import io
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple


KEYWORD_CONDITIONS = {
    "fever": "Viral Fever",
    "cough": "Upper Respiratory Infection",
    "cold": "Common Cold",
    "headache": "Migraine",
    "chest pain": "Cardiac Concern",
    "high sugar": "Diabetes",
    "thirst": "Diabetes",
    "fatigue": "Anemia / Metabolic Stress",
    "breath": "Respiratory Concern",
    "palpitations": "Cardiac Arrhythmia Concern",
}

EMERGENCY_KEYWORDS = {
    "chest pain",
    "difficulty breathing",
    "shortness of breath",
    "fainting",
    "stroke",
    "seizure",
    "unconscious",
    "severe bleeding",
}

CONDITION_TO_SPECIALIST = {
    "Diabetes": "Endocrinologist",
    "Cardiac Concern": "Cardiologist",
    "Cardiac Arrhythmia Concern": "Cardiologist",
    "Upper Respiratory Infection": "Pulmonologist",
    "Common Cold": "General Physician",
    "Viral Fever": "General Physician",
    "Migraine": "Neurologist",
    "Respiratory Concern": "Pulmonologist",
    "Anemia / Metabolic Stress": "Internal Medicine Specialist",
}


def triage_message(message: str, symptoms: List[str]) -> Tuple[str, List[str], str, str | None]:
    combined = f"{message} {' '.join(symptoms)}".lower()

    possible_conditions: List[str] = []
    for keyword, condition in KEYWORD_CONDITIONS.items():
        if keyword in combined:
            possible_conditions.append(condition)

    if not possible_conditions:
        possible_conditions = ["General Health Concern"]

    emergency_hit = any(kw in combined for kw in EMERGENCY_KEYWORDS)
    urgency = "emergency" if emergency_hit else "normal"

    common = Counter(possible_conditions).most_common(1)[0][0]
    specialist = CONDITION_TO_SPECIALIST.get(common, "General Physician")

    if urgency == "emergency":
        response = (
            "Your symptoms may indicate an emergency. Please call local emergency services "
            "or visit the nearest emergency room immediately."
        )
    else:
        conditions_str = ", ".join(sorted(set(possible_conditions)))
        response = (
            f"Based on your input, possible issues include: {conditions_str}. "
            f"For an accurate diagnosis, consult a {specialist}."
        )

    return response, sorted(set(possible_conditions)), urgency, specialist


def parse_medical_report(file_name: str, raw_bytes: bytes) -> Dict[str, str | List[str]]:
    text_blob = ""
    alerts: List[str] = []

    if file_name.lower().endswith(".csv"):
        decoded = raw_bytes.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(decoded))
        flattened = [" ".join(row) for row in reader]
        text_blob = " ".join(flattened)
    else:
        text_blob = raw_bytes.decode("utf-8", errors="ignore")

    normalized = text_blob.lower()

    glucose_match = re.search(r"glucose\D+(\d+)", normalized)
    if glucose_match and int(glucose_match.group(1)) > 180:
        alerts.append("High glucose detected; diabetes evaluation is recommended.")

    bp_match = re.search(r"blood pressure\D+(\d{2,3})/(\d{2,3})", normalized)
    if bp_match:
        sys = int(bp_match.group(1))
        dia = int(bp_match.group(2))
        if sys >= 140 or dia >= 90:
            alerts.append("Elevated blood pressure observed; consult a cardiologist.")

    chol_match = re.search(r"cholesterol\D+(\d+)", normalized)
    if chol_match and int(chol_match.group(1)) > 240:
        alerts.append("High cholesterol level detected; lipid management advised.")

    summary = (
        "Automated report scan completed. "
        "This tool provides educational guidance and should not replace physician review."
    )

    if not alerts:
        alerts.append("No critical flags found in uploaded content.")

    return {"summary": summary, "alerts": alerts}


def generate_recommendations(conditions: List[str]) -> Dict[str, List[str]]:
    base = {
        "diet": [
            "Include more vegetables, lean proteins, and whole grains.",
            "Limit high-sugar and highly processed foods.",
        ],
        "lifestyle": [
            "Sleep 7-8 hours daily.",
            "Hydrate with at least 2-3 liters of water unless advised otherwise.",
        ],
        "exercises": [
            "Brisk walking for 30 minutes, 5 times per week.",
            "Light stretching or yoga for 15 minutes daily.",
        ],
        "home_remedies": [
            "For mild cold/cough, use warm fluids and steam inhalation.",
            "For mild fever, prioritize hydration and rest.",
        ],
        "otc_medicines": [
            "Only use over-the-counter medicines after checking labels and contraindications.",
            "Avoid self-medication if pregnant, elderly, or managing chronic disease.",
        ],
    }

    if "Diabetes" in conditions:
        base["diet"].append("Prefer low glycemic index meals and monitor carbohydrate portions.")
        base["lifestyle"].append("Track fasting and post-meal blood sugar trends.")

    if "Cardiac Concern" in conditions or "Cardiac Arrhythmia Concern" in conditions:
        base["diet"].append("Reduce sodium intake and avoid trans fats.")
        base["exercises"].append("Choose moderate-intensity exercise after medical clearance.")

    return base


def now_iso() -> datetime:
    return datetime.utcnow()
