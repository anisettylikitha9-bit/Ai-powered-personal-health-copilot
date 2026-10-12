"""
symptom_checker.py - Rule-Based Symptom Triage, Red-Flag Emergency Detection,
and Safe Next-Step Health Guidance Engine.
Strictly non-diagnostic; provides triage safety and India 112 emergency routing.
"""

from typing import List, Dict, Any, Tuple

# Critical Red Flag Emergency Symptoms
RED_FLAG_SYMPTOMS = [
    "Severe Chest Pain or Pressure",
    "Difficulty Breathing / Severe Shortness of Breath",
    "Sudden Weakness / Numbness on One Side of Body",
    "Slurred Speech or Difficulty Speaking",
    "Sudden Loss of Vision",
    "Coughing up Blood",
    "Severe Allergic Reaction (Swollen lips/tongue, wheezing)",
    "Severe Head Injury or Loss of Consciousness",
    "High Fever (>103°F) with Stiff Neck or Confusion"
]

COMMON_SYMPTOMS_LIST = [
    "Mild to Moderate Fever",
    "Headache",
    "Sore Throat",
    "Dry or Productive Cough",
    "Runny or Stuffy Nose",
    "Body Aches or Muscle Pain",
    "Fatigue / General Tiredness",
    "Mild Nausea or Upset Stomach",
    "Diarrhea / Loose Stools",
    "Mild Indigestion or Heartburn",
    "Mild Joint Pain",
    "Minor Skin Rash / Itching",
    "Mild Anxiety / Stress"
]

DURATION_CHOICES = [
    "Less than 24 hours",
    "1 to 3 days",
    "4 to 7 days",
    "More than 1 week",
    "More than 2 weeks"
]

SEVERITY_CHOICES = [
    "Mild (Noticeable but does not affect daily activities)",
    "Moderate (Interferes with some daily activities)",
    "Severe (Significantly debilitating, unable to perform daily tasks)"
]


def assess_symptoms(
    selected_symptoms: List[str],
    duration: str,
    severity: str,
    additional_notes: str = ""
) -> Dict[str, Any]:
    """
    Evaluates reported symptoms, checks for critical red-flag emergency signs,
    and returns safe educational next steps and consultation guidance.
    """
    is_emergency = False
    emergency_reasons = []

    # Check for red flags
    for symp in selected_symptoms:
        if symp in RED_FLAG_SYMPTOMS:
            is_emergency = True
            emergency_reasons.append(symp)

    notes_lower = additional_notes.lower()
    emergency_phrases = ["chest pain", "can't breathe", "cannot breathe", "fainted", "unconscious", "stroke", "bleeding profusely"]
    for phrase in emergency_phrases:
        if phrase in notes_lower:
            is_emergency = True
            emergency_reasons.append(f"Noted: '{phrase}'")

    if "severe" in severity.lower() and ("fever" in " ".join(selected_symptoms).lower() or "headache" in " ".join(selected_symptoms).lower()):
        if duration in ["More than 1 week", "More than 2 weeks"]:
            is_emergency = True
            emergency_reasons.append("Severe symptoms persisting beyond 1 week")

    if is_emergency:
        return {
            "is_emergency": True,
            "emergency_reasons": emergency_reasons,
            "headline": "🚨 POTENTIAL MEDICAL EMERGENCY DETECTED",
            "emergency_number": "112 (India General Emergency) | 108 (Ambulance)",
            "urgent_actions": [
                "Stop any physical exertion immediately and rest in a comfortable, safe position.",
                "Call 112 or 108 immediately, or have someone accompany you to the nearest Emergency Department (Casualty).",
                "Do not drive yourself to the hospital.",
                "Keep your medical ID, emergency contact, and current medication list accessible."
            ],
            "disclaimer": "This tool is not a diagnostic device. If you feel your health is in acute danger, do not wait for online tools—seek emergency medical attention immediately."
        }

    # Educational Next Steps for Non-Emergency Symptoms
    self_care_tips = [
        "Rest & Recovery: Allow your body adequate rest and minimize strenuous physical activities.",
        "Hydration: Drink plenty of clean fluids (warm water, broths, electrolyte water, or herbal tea).",
        "Symptom Diary: Note your body temperature, symptoms, and meal times in this app to share with your doctor."
    ]

    doctor_advice = []
    if "fever" in " ".join(selected_symptoms).lower():
        doctor_advice.append("For fever lasting more than 3 days or exceeding 102°F, consult a physician for diagnostic evaluation.")
    if "cough" in " ".join(selected_symptoms).lower() or "throat" in " ".join(selected_symptoms).lower():
        doctor_advice.append("If cough is accompanied by shortness of breath, colored phlegm, or lasts over 2 weeks, consult a pulmonologist or general physician.")
    if "stomach" in " ".join(selected_symptoms).lower() or "diarrhea" in " ".join(selected_symptoms).lower():
        doctor_advice.append("Stay hydrated with oral rehydration salts (ORS). If unable to retain liquids for over 24 hours, seek prompt medical care.")
    if not doctor_advice:
        doctor_advice.append("If symptoms worsen, do not improve within 3 to 5 days, or interfere with normal eating and sleeping, schedule a primary care visit.")

    return {
        "is_emergency": False,
        "emergency_reasons": [],
        "headline": "Safe Educational Next-Step Guidance",
        "severity_summary": f"Reported: {', '.join(selected_symptoms) if selected_symptoms else 'None specified'} ({severity}, {duration})",
        "self_care_tips": self_care_tips,
        "doctor_advice": doctor_advice,
        "disclaimer": "Notice: The Symptom Checker is strictly an informational tool to assist in organizing your health concerns. It does not replace professional clinical diagnosis, physical examination, or laboratory investigation. Never disregard medical advice based on this tool."
    }
