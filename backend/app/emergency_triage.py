"""
backend/app/emergency_triage.py - Three-Tier Clinical Urgency Triage System
Safety Requirements:
- Strictly conservative, validated clinical rules.
- Evaluates Tier 1 red flags BEFORE any ordinary health advice.
- Does NOT diagnose diseases or name definitive pathologies.
- Never treats lack of detected keywords as proof of safety.
- Never delays emergency guidance with unnecessary questions.
- Clearly states that assessment is not a medical diagnosis.
"""

from typing import Dict, Any, List, Optional
try:
    from backend.app.language_support import get_text, get_disclaimer
except ImportError:
    from .language_support import get_text, get_disclaimer

# ==============================================================================
# TIER 1: EMERGENCY CARE NOW (RED-FLAG RULES - INDIA 112 / 108)
# ==============================================================================

RED_FLAG_PATTERNS = [
    {
        "id": "EMERGENCY_CHEST_CARDIAC",
        "category": "Cardiac / Acute Chest Pain",
        "keywords": [
            "chest pain", "chest pressure", "heart attack", "crushing chest",
            "chest tightness", "pain radiating to arm", "left arm pain", "pain in jaw",
            "ఛాతీ నొప్పి", "గుండెపోటు", "ఛాతీలో నొప్పి", "గుండె నొప్పి",
            "gunde noppi", "chati noppi", "chaati noppi", "chathilo noppi", "gunde potu"
        ],
        "description_en": "Severe or concerning chest pain/pressure potentially indicating acute cardiac compromise.",
        "description_te": "తీవ్రమైన ఛాతీ నొప్పి లేదా ఒత్తిడి, ఇది గుండె సంబంధిత అత్యవసర పరిస్థితిని సూచించవచ్చు.",
        "description_roman": "Teevramaina chati noppi leda gunde sambhandhita acute emergency."
    },
    {
        "id": "EMERGENCY_BREATHING",
        "category": "Severe Respiratory Distress",
        "keywords": [
            "difficulty breathing", "severe shortness of breath", "cannot breathe", "can't breathe",
            "struggling to breathe", "gasping for air", "choking", "turning blue", "cyanosis",
            "శ్వాస తీసుకోవడంలో ఇబ్బంది", "శ్వాస ఆడటం లేదు", "ఉబ్బసం తీవ్రం",
            "oopiri aadatledu", "oopiri aadatam ledu", "swasa aadatledu", "swasa kastam", "gali aadatledu"
        ],
        "description_en": "Severe breathing difficulty, acute shortness of breath, or respiratory exhaustion.",
        "description_te": "తీవ్రమైన శ్వాసకోశ సమస్య లేదా గాలి సరిగా తీసుకోలేకపోవడం.",
        "description_roman": "Teevramaina swasa samasya leda oopiri aadanappudu emergency paristhithi."
    },
    {
        "id": "EMERGENCY_STROKE_FAST",
        "category": "Possible Stroke Warning Signs (F.A.S.T.)",
        "keywords": [
            "facial drooping", "face droop", "slurred speech", "difficulty speaking", "cannot speak",
            "weakness on one side", "paralysis on one side", "numbness on one side", "stroke",
            "ముఖం వంకరపోవడం", "మాట తడబడటం", "ఒక వైపు బలహీనత", "పక్షవాతం",
            "mata thadabadatam", "mata ravatledu", "mukham vankara", "pakshavatham", "oka vaipu cheyyi laagatledu"
        ],
        "description_en": "Possible acute stroke warning signs (facial drooping, unilateral arm weakness, speech slurring).",
        "description_te": "పక్షవాత హెచ్చరిక సంకేతాలు (ముఖం వంకర, మాట తడబడటం, ఒక వైపు బలహీనత).",
        "description_roman": "Stroke / Pakshavatham sankethalu (mukham vankara, cheyyi balheenatha, mata thadabadatam)."
    },
    {
        "id": "EMERGENCY_UNCONSCIOUS",
        "category": "Unconsciousness / Severe Syncope",
        "keywords": [
            "unconscious", "loss of consciousness", "fainted with head injury", "passed out",
            "blacked out and fell", "unresponsive", "స్పృహ కోల్పోవడం", "స్పృహ తప్పి పడిపోవడం",
            "spruha thappindi", "spruha ledhu", "kallu thirigi padipoyadu", "telivi thappindi"
        ],
        "description_en": "Unconsciousness, unresponsiveness, or traumatic syncopal collapse.",
        "description_te": "స్పృహ కోల్పోవడం లేదా తలకు గాయం తర్వాత స్పృహ తప్పి పడిపోవడం.",
        "description_roman": "Spruha thappadam leda thalaku gaayam tharuvatha spruha kolpovadam."
    },
    {
        "id": "EMERGENCY_BLEEDING",
        "category": "Severe Uncontrolled Bleeding",
        "keywords": [
            "severe bleeding", "bleeding profusely", "coughing up blood", "vomiting blood",
            "blood in vomit", "hemoptysis", "రక్తం కారడం", "రక్తం వాంతి", "దగ్గులో రక్తం",
            "raktham kaaruthondi", "raktham vanthi", "daggulo raktham", "raktham paduthondi"
        ],
        "description_en": "Severe, uncontrolled active hemorrhage or coughing/vomiting blood.",
        "description_te": "తీవ్రమైన నియంత్రణ లేని రక్తస్రావం లేదా దగ్గు/వాంతిలో రక్తం పడటం.",
        "description_roman": "Teevramaina aagani rakthasravam leda daggulo/vanthilo raktham padatam."
    }
]


def detect_emergency(text: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """
    Scans input for high-priority Tier 1 red flags.
    Returns structured emergency report if any red flag matches.
    """
    clean_lower = text.lower().strip()
    for rule in RED_FLAG_PATTERNS:
        for kw in rule["keywords"]:
            if kw in clean_lower:
                desc = rule["description_en"]
                if lang == "te":
                    desc = rule.get("description_te", desc)
                elif lang == "te-roman":
                    desc = rule.get("description_roman", desc)
                
                return {
                    "rule_id": rule["id"],
                    "matched_category": rule["category"],
                    "keyword": kw,
                    "description": desc,
                    "headline": get_text("emergency_headline", lang),
                    "emergency_number": "112 (India General Emergency) / 108 (Ambulance)",
                    "urgent_actions": [
                        "Stop all physical exertion immediately. Sit or lie down in a safe position.",
                        "Call 112 or 108 immediately, or have someone take you to the nearest Emergency Casualty.",
                        "Do NOT drive yourself to the hospital.",
                        "Do NOT wait for a chatbot response or delay emergency care."
                    ],
                    "limitations": "Safety Rule: The absence of detected keywords does NOT prove safety. If you feel in acute danger, seek emergency medical care immediately."
                }
    return None


def evaluate_three_tier_triage(
    symptoms: List[str],
    text_input: str = "",
    severity: str = "Moderate",
    duration: str = "1 to 3 days",
    age: Optional[int] = None,
    gender: Optional[str] = None,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Evaluates reported condition across three clinical urgency tiers:
    1. 'Emergency care now' (Severe breathing difficulty, stroke signs, unconsciousness, chest pain, uncontrolled bleeding -> 112)
    2. 'Prompt medical consultation' (Persistent >3 days, severe intensity, co-occurring concerns requiring physician evaluation)
    3. 'General self-care guidance' (Mild, early-stage, low-risk concerns without detected red flags)
    """
    combined_text = (text_input + " " + " ".join(symptoms)).lower()

    # --- TIER 1: EMERGENCY CARE NOW CHECK ---
    emergency_match = detect_emergency(combined_text, lang=lang)
    if emergency_match:
        return {
            "tier": "Emergency care now",
            "tier_level": 1,
            "badge_color": "rose",
            "headline": emergency_match["headline"],
            "call_to_action": get_text("emergency_cta", lang),
            "emergency_numbers": ["112 (India General Emergency)", "108 (Free Emergency Ambulance)"],
            "category": emergency_match["matched_category"],
            "reasons": [emergency_match["description"]],
            "urgent_actions": emergency_match["urgent_actions"],
            "limitation": emergency_match["limitations"]
        }

    # --- TIER 2: PROMPT MEDICAL CONSULTATION CHECK ---
    is_persistent = duration in ["4 to 7 days", "More than 1 week", "More than 2 weeks", "More than a week"]
    is_severe = "severe" in severity.lower()
    has_multiple_symptoms = len(symptoms) >= 3
    concerning_terms = ["fever", "vomit", "dizzy", "pain", "rash", "weight loss", "stomach", "cough"]
    matches_concerning = sum(1 for term in concerning_terms if term in combined_text) >= 2

    if is_severe or is_persistent or has_multiple_symptoms or matches_concerning:
        reasons_list = []
        if is_severe:
            reasons_list.append("Reported symptom intensity is severe, interfering with daily activities.")
        if is_persistent:
            reasons_list.append(f"Symptoms have persisted for {duration}, warranting clinical investigation.")
        if has_multiple_symptoms:
            reasons_list.append(f"Multiple concurrent symptoms reported ({', '.join(symptoms[:3])}).")
        if not reasons_list:
            reasons_list.append("Reported symptoms require timely clinical evaluation by a medical doctor.")

        return {
            "tier": "Prompt medical consultation",
            "tier_level": 2,
            "badge_color": "amber",
            "headline": get_text("prompt_consult_headline", lang),
            "call_to_action": get_text("prompt_consult_cta", lang),
            "emergency_numbers": ["112 (Emergency Hotline)"],
            "category": "Persistent / Concerning Health Symptoms",
            "reasons": reasons_list,
            "urgent_actions": [
                "Schedule an in-person or telemedicine appointment with a licensed General Physician.",
                "Maintain a written log of symptom progression, temperature readings, and time of onset.",
                "Rest adequately and stay hydrated; do not take unprescribed antibiotics or strong painkillers.",
                "If any red flags arise (e.g. chest tightness, sudden shortness of breath, fainting), call 112 immediately."
            ],
            "limitation": "Clinical Disclaimer: This rule-based triage assessment organizes health information for medical discussion. It is not an official medical diagnosis, laboratory test, or pathology report."
        }

    # --- TIER 3: GENERAL SELF-CARE GUIDANCE ---
    return {
        "tier": "General self-care guidance",
        "tier_level": 3,
        "badge_color": "emerald",
        "headline": get_text("self_care_headline", lang),
        "call_to_action": get_text("self_care_cta", lang),
        "emergency_numbers": ["112 (India Emergency)"],
        "category": "Mild / Early-Stage Wellness Management",
        "reasons": [
            "Reported symptoms appear mild in intensity with short duration.",
            "No acute red-flag emergency indicators detected in conservative triage rules."
        ],
        "urgent_actions": [
            "Prioritize restorative rest (7 to 9 hours) to allow your immune system to recuperate.",
            "Stay well hydrated with clean water, warm broths, or oral rehydration fluids.",
            "Record your daily temperature, meals, and sleep in the Wellness Tracker.",
            "If symptoms worsen, persist beyond 3 days, or new pain develops, consult a doctor."
        ],
        "limitation": "Informational Notice: The absence of detected emergency indicators does not guarantee that a serious condition is not present. Always listen to your body and consult a physician if in doubt."
    }
