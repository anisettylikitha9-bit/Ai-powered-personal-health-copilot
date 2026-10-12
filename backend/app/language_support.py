"""
backend/app/language_support.py - Multilingual Health Companion Engine
Provides localized templates, translations, and safe emergency strings
for English (en), తెలుగు (te), and Roman Telugu (te-roman).
"""

from typing import Dict, Any, Optional

DISCLAIMER_EN = (
    "\n\n---\n⚕️ *Medical Disclaimer: HealthSaathi AI is an educational wellness tool and personal health log. "
    "It is NOT a doctor and CANNOT diagnose medical conditions or prescribe drugs. "
    "For severe or worsening symptoms, consult a qualified medical professional immediately. "
    "In acute medical emergencies, call India's emergency number 112.*"
)

DISCLAIMER_TE = (
    "\n\n---\n⚕️ *వైద్య గమనిక: హెల్త్‌సాథి AI అనేది విద్యాపరమైన వెల్‌నెస్ సాధనం మరియు వ్యక్తిగత ఆరోగ్య లాగ్ మాత్రమే. "
    "ఇది వైద్యుడు కాదు మరియు వ్యాధులను నిర్ధారించలేదు లేదా మందులను సూచించలేదు. "
    "తీవ్రమైన లక్షణాల కోసం అర్హత కలిగిన వైద్యుడిని సంప్రదించండి. అత్యవసర పరిస్థితుల్లో వెంటనే 112 కు కాల్ చేయండి.*"
)

DISCLAIMER_ROMAN = (
    "\n\n---\n⚕️ *Medical Gamanika: HealthSaathi AI kevalam vidya mariyu personal wellness log matrame. "
    "Ee assistant doctor kaadu mariyu rogala nirdharana (diagnosis) cheyyadu leda mandulu ivvadu. "
    "Theevramaina lakshanalu unte ventane doctor ni kalavali. Emergency unte ventane 112 ku call cheyyandi.*"
)

TRANSLATIONS_MAP: Dict[str, Dict[str, str]] = {
    "en": {
        "emergency_headline": "🚨 EMERGENCY CARE NOW (DO NOT WAIT)",
        "emergency_cta": "Call 112 (India Emergency) or 108 (Ambulance) IMMEDIATELY.",
        "emergency_warning": "Do not wait for a chatbot response. Proceed to the nearest emergency department.",
        "prompt_consult_headline": "⚠️ PROMPT MEDICAL CONSULTATION RECOMMENDED",
        "prompt_consult_cta": "Schedule an appointment with a General Physician within 24 to 48 hours.",
        "self_care_headline": "💚 GENERAL SELF-CARE & HOME MONITORING GUIDANCE",
        "self_care_cta": "Monitor symptoms with restorative home self-care practices.",
        "unclear_prompt": "Please describe your symptoms with duration and intensity (e.g., 'I have a headache since yesterday').",
        "greeting": "Hello! I am HealthSaathi AI, your personal health and symptom educational assistant. How can I assist you today?"
    },
    "te": {
        "emergency_headline": "🚨 అత్యవసర వైద్య సంరక్షణ తక్షణమే అవసరం (వేచి ఉండకండి)",
        "emergency_cta": "వెంటనే 112 (భారత అత్యవసర నంబర్) లేదా 108 కు కాల్ చేయండి.",
        "emergency_warning": "చాట్‌బాట్ ప్రతిస్పందన కోసం వేచి ఉండకండి. వెంటనే సమీపంలోని అత్యవసర ఆసుపత్రికి వెళ్లండి.",
        "prompt_consult_headline": "⚠️ వెంటనే వైద్యుడిని సంప్రదించడం సిఫార్సు చేయబడింది",
        "prompt_consult_cta": "24 నుండి 48 గంటల్లో సాధారణ వైద్యుడిని (General Physician) సంప్రదించండి.",
        "self_care_headline": "💚 సాధారణ స్వీయ సంరక్షణ మరియు పర్యవేక్షణ",
        "self_care_cta": "విశ్రాంతి, తగినంత నీరు మరియు తేలికపాటి స్వీయ సంరక్షణతో లక్షణాలను గమనించండి.",
        "unclear_prompt": "దయచేసి మీ లక్షణాలను కొద్దిగా వివరంగా తెలియజేయండి (ఉదా: 'నాకు నిన్నటి నుండి తలనొప్పి ఉంది').",
        "greeting": "నమస్కారం! నేను హెల్త్‌సాథి AI, మీ వ్యక్తిగత ఆరోగ్య సహాయకుడిని. ఈరోజు నేను మీకు ఎలా సహాయపడగలను?"
    },
    "te-roman": {
        "emergency_headline": "🚨 EMERGENCY CARE NOW (DO NOT WAIT)",
        "emergency_cta": "Ventane 112 (India Emergency) leda 108 (Ambulance) ku call cheyyandi.",
        "emergency_warning": "Chatbot response kosam aagakandi. Ventane nearest emergency hospital ki vellali.",
        "prompt_consult_headline": "⚠️ PROMPT MEDICAL CONSULTATION RECOMMENDED",
        "prompt_consult_cta": "24 nundi 48 hours lo General Physician doctor ni kalavali.",
        "self_care_headline": "💚 GENERAL SELF-CARE & HOME MONITORING GUIDANCE",
        "self_care_cta": "Manchi rest theesukondi, neellu thagandi mariyu symptoms ni monitor cheyyandi.",
        "unclear_prompt": "Dhayachesi mee lakshanala gurinchi konchem vivaramga cheppandi (e.g. 'Naaku ninnati nundi thala noppi undi').",
        "greeting": "Namaskaram! Nenu HealthSaathi AI, mee personal health companion. Eeroju meeku elaa sahayam cheyagalanu?"
    }
}


def get_disclaimer(lang: str = "en") -> str:
    """Returns statutory non-diagnostic disclaimer in requested language."""
    if lang == "te":
        return DISCLAIMER_TE
    elif lang == "te-roman":
        return DISCLAIMER_ROMAN
    return DISCLAIMER_EN


def get_text(key: str, lang: str = "en") -> str:
    """Retrieves localized text with English fallback."""
    target_dict = TRANSLATIONS_MAP.get(lang, TRANSLATIONS_MAP["en"])
    return target_dict.get(key, TRANSLATIONS_MAP["en"].get(key, key))
