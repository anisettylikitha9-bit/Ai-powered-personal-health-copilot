"""
backend/app/assistant.py - Smart Conversational Health Assistant
Provides transparent rule-based clinical guidance, multilingual support (English, Telugu, Roman Telugu),
high-priority emergency triage checks, non-prescriptive medication guards, and optional local LLM integration.
Does NOT require paid APIs, external services, or API keys. 100% offline-functional.
"""

import os
import re
import urllib.request
import json
from typing import Dict, Any, List, Optional
try:
    from backend.app.emergency_triage import detect_emergency
    from backend.app.language_support import get_disclaimer, get_text
except ImportError:
    from .emergency_triage import detect_emergency
    from .language_support import get_disclaimer, get_text

# ==============================================================================
# CLINICAL LIFESTYLE & SYMPTOM KNOWLEDGE BASE
# ==============================================================================

KNOWLEDGE_RULES = [
    {
        "id": "RULE_DEHYDRATION",
        "keywords": ["dehydration", "dehydrated", "explain dehydration", "neeti koratha", "dehydration in telugu", "dehydration gurinchi"],
        "category": "Dehydration Management",
        "title": "Dehydration: Science, Warning Signs & Oral Rehydration",
        "response_en": (
            "💧 **Clinical Overview of Dehydration:**\n\n"
            "• **What is Dehydration?**: Occurs when your body loses more fluids and electrolytes than you take in, disrupting metabolic and cellular homeostasis.\n"
            "• **Key Warning Signs**:\n"
            "  - Intense thirst and parched, dry mouth or lips.\n"
            "  - Infrequent urination or dark amber/brown-tinted urine.\n"
            "  - Lightheadedness, dizziness, or orthostatic fainting upon standing.\n"
            "  - Muscle cramps, persistent lethargy, and mild headaches.\n"
            "• **Safe Home Recovery Steps**:\n"
            "  - Drink Oral Rehydration Solution (ORS), tender coconut water, or clean water with a pinch of salt and lemon.\n"
            "  - Sip fluids steadily rather than gulping large amounts at once.\n"
            "  - Avoid sugary sodas, concentrated juices, alcohol, and excessive caffeine.\n"
            "• **Emergency Red Flags (Seek Care Now)**:\n"
            "  - Inability to retain any liquids for > 12 hours, extreme confusion, or fainting (Call 112)."
        ),
        "response_te": (
            "💧 **శరీరంలో నీటి కొరత (డీహైడ్రేషన్) సమగ్ర వివరణ:**\n\n"
            "• **డీహైడ్రేషన్ అంటే ఏమిటి?**: మన శరీరం గ్రహించే ద్రవాల కంటే ఎక్కువ నీరు, ఎలక్ట్రోలైట్లను కోల్పోయినప్పుడు డీహైడ్రేషన్ సంభవిస్తుంది.\n"
            "• **ముఖ్య లక్షణాలు**:\n"
            "  - తీవ్రమైన దాహం, పెదవులు మరియు నోరు ఎండిపోవడం.\n"
            "  - మూత్రం చాలా తక్కువగా రావడం లేదా ముదురు పసుపు రంగులో ఉండటం.\n"
            "  - కళ్ళు తిరగడం, తలనొప్పి, నీరసం మరియు కండరాల నొప్పులు.\n"
            "• **సురక్షితమైన నివారణ మరియు సంరక్షణ చర్యలు**:\n"
            "  - వెంటనే ఓఆర్ఎస్ (ORS) ద్రావణం, తాజా కొబ్బరి నీరు లేదా నిమ్మకాయ నీరు తాగండి.\n"
            "  - ఎండలో తిరగడం ఆపి, చల్లని ప్రదేశంలో విశ్రాంతి తీసుకోండి; మజ్జిగ శరీరానికి చాలా మేలు చేస్తుంది.\n"
            "  - శీతల పానీయాలు (కూల్ డ్రింక్స్) మరియు ఆల్కహాల్‌కు దూరంగా ఉండండి.\n"
            "• **అత్యవసర హెచ్చరిక**: నిరంతర వాంతులు లేదా స్పృహ తప్పితే వెంటనే ఆసుపత్రికి వెళ్లండి (112)."
        ),
        "response_roman": (
            "💧 **Dehydration (Neeti Koratha) Vivarana:**\n\n"
            "• **Dehydration Ante Enti?**: Mana shareeram theesukune dravamula kante ekkuva neellu mariyu electrolytes kolpoyinappudu dehydration avuthundi.\n"
            "• **Mukhyamaina Lakshanalu**:\n"
            "  - Theevramaina daaham mariyu noru endipovadam.\n"
            "  - Moodhra rangam muduru pasupu rangulo undatam leda thakkuvaga ravadam.\n"
            "  - Kallu thiragadam, thala noppi, mariyu neerasam.\n"
            "• **Nivarana Mariyu Care Tips**:\n"
            "  - Ventane ORS fluid, fresh kobbari neellu, leda manchineellu thagandi.\n"
            "  - Majjiga theesukondi mariyu cool environment lo rest theesukondi.\n"
            "  - Cool drinks mariyu tea/coffee thagakandi.\n"
            "• **Emergency Note**: 12 hours nunchi fluids aagakapothe leda kallu thirigi padipothe ventane hospital ki vellali (Call 112)."
        ),
        "follow_ups": [
            "What are the best fluids for dehydration?",
            "How much water should I drink daily?",
            "Signs of severe dehydration"
        ]
    },
    {
        "id": "RULE_HEADACHE",
        "keywords": ["headache", "head ache", "head pain", "migraine", "thala noppi", "thalanopi", "తలనొప్పి", "తలనొప్పిగా ఉంది"],
        "category": "Headache & Tension Management",
        "title": "Headache: Educational Causes, Safe Relief & Red Flags",
        "response_en": (
            "🤕 **Educational Overview of Headaches:**\n\n"
            "• **Common Possibilities**: Tension headache (stress/screen fatigue), dehydration, eye strain, lack of sleep, or sinus pressure.\n"
            "• **Safe Self-Care Next Steps**:\n"
            "  - Drink 2 glasses of water (mild dehydration is a leading headache trigger).\n"
            "  - Rest in a quiet, dimly lit room for 30–45 minutes away from screens.\n"
            "  - Apply a cool damp cloth across your forehead or back of the neck.\n"
            "  - Practice slow rhythmic breathing to reduce muscular cervical tension.\n"
            "• **When to Seek Prompt Doctor Consultation**:\n"
            "  - Pain persists for > 48 hours or progressively worsens.\n"
            "  - Accompanied by high fever, stiff neck, or visual aura.\n"
            "• **🚨 Emergency Warning (Call 112 Now)**:\n"
            "  - Sudden, severe 'thunderclap' headache (worst headache of your life), numbness on one side, confusion, or speech slurring."
        ),
        "response_te": (
            "🤕 **తలనొప్పిపై సమగ్ర విద్యా సమాచారం & స్వీయ సంరక్షణ:**\n\n"
            "• **సాధారణ కారణాలు**: మానసిక ఒత్తిడి, ఎక్కువ సేపు స్క్రీన్ చూడటం, నిద్రలేమి లేదా శరీరంలో నీటి కొరత (డీహైడ్రేషన్).\n"
            "• **సురక్షితమైన స్వీయ సంరక్షణ చర్యలు**:\n"
            "  - వెంటనే 1-2 గ్లాసుల మంచినీరు తాగండి.\n"
            "  - మొబైల్/ల్యాప్‌టాప్ స్క్రీన్ల నుండి దూరంగా, నిశ్శబ్దమైన చీకటి గదిలో విశ్రాంతి తీసుకోండి.\n"
            "  - నుదుటిపై చల్లటి గుడ్డను ఉంచి కొద్దిసేపు విశ్రాంతి తీసుకోండి.\n"
            "• **వైద్యుడిని ఎప్పుడు సంప్రదించాలి**:\n"
            "  - తలనొప్పి 2 రోజుల కంటే ఎక్కువ కొనసాగితే లేదా తీవ్ర జ్వరం, మెడ పట్టేయడం వంటి లక్షణాలు ఉంటే.\n"
            "• **🚨 అత్యవసర హెచ్చరిక**: అకస్మాత్తుగా తీవ్రమైన తలనొప్పి వస్తే, మాట తడబడితే లేదా ఒక వైపు చేయి బలహీనపడితే వెంటనే 112 కు కాల్ చేయండి."
        ),
        "response_roman": (
            "🤕 **Thala Noppi (Headache) Vivarana & Care Tips:**\n\n"
            "• **Sadharana Karanamulu**: Stress, ekkuva sepu mobile choodatam, nidralemi leda neellu thakkuvaga thagadam.\n"
            "• **Safe Home Care Tips**:\n"
            "  - Ventane 1-2 glasses manchineellu thagandi.\n"
            "  - Screen vadilesi calm ga unna room lo rest theesukondi.\n"
            "  - Nudhutipai challani cloth unchi konchem relax avvandi.\n"
            "• **Doctor Ni Eppudu Kalavali**:\n"
            "  - 2 days nundi thala noppi thaggakapothe leda high fever unte.\n"
            "• **🚨 Emergency Alert**: Aakasmikamga theevramaina thala noppi vachi mata thadabadithe ventane 112 ku call cheyyandi."
        ),
        "follow_ups": [
            "How can I tell if my headache is from dehydration?",
            "When should I see a doctor for headache?",
            "Safe home remedies without tablets"
        ]
    },
    {
        "id": "RULE_FEVER",
        "keywords": ["fever", "temperature", "pyrexia", "jwaram", "jwaranga undi", "naaku jwaram", "జ్వరం", "జ్వరంగా ఉంది", "వేడి"],
        "category": "Fever & Thermoregulation",
        "title": "Fever: Monitoring, Safe Hydration & Clinical Thresholds",
        "response_en": (
            "🌡️ **Educational Overview of Fever:**\n\n"
            "• **What is Fever?**: Fever is an adaptive immune defense response where your brain temporarily resets body temperature to fight infection.\n"
            "• **Safe Home Care**:\n"
            "  - Check temperature with an oral or axillary digital thermometer and record readings.\n"
            "  - Rest adequately; wear light, breathable cotton clothing.\n"
            "  - Stay well-hydrated with water, coconut water, and warm broths to prevent dehydration.\n"
            "  - Use lukewarm (not cold) sponge baths if uncomfortable.\n"
            "• **When to See a Doctor**:\n"
            "  - Fever > 102°F (38.9°C) or lasting > 3 consecutive days.\n"
            "  - Accompanied by severe throat pain, rash, burning urination, or persistent vomiting.\n"
            "• **🚨 Emergency Warning (Call 112)**:\n"
            "  - Severe breathing difficulty, chest pain, lethargy/unresponsiveness, or stiff neck."
        ),
        "response_te": (
            "🌡️ **జ్వరం సమగ్ర విశ్లేషణ & స్వీయ సంరక్షణ సూచనలు:**\n\n"
            "• **జ్వరం అంటే ఏమిటి?**: మన శరీరం ఇన్‌ఫెక్షన్‌లతో పోరాడుతున్నప్పుడు రోగనిరోధక వ్యవస్థ శరీర ఉష్ణోగ్రతను పెంచుతుంది.\n"
            "• **సురక్షితమైన స్వీయ సంరక్షణ**:\n"
            "  - థర్మామీటర్‌తో ఉష్ణోగ్రతను కొలవండి మరియు సమయాన్ని నమోదు చేయండి.\n"
            "  - తేలికపాటి కాటన్ దుస్తులు ధరించి మంచి విశ్రాంతి తీసుకోండి.\n"
            "  - శరీరం డీహైడ్రేట్ కాకుండా పుష్కలంగా నీరు, కొబ్బరి నీరు, మజ్జిగ తాగండి.\n"
            "• **వైద్యుడిని ఎప్పుడు సంప్రదించాలి**:\n"
            "  - జ్వరం 102°F దాటినా లేదా 3 రోజుల కంటే ఎక్కువ కొనసాగినా.\n"
            "• **🚨 అత్యవసర హెచ్చరిక**: శ్వాస తీసుకోవడంలో ఇబ్బంది, స్పృహ తప్పడం ఉంటే వెంటనే 112 కు కాల్ చేయండి."
        ),
        "response_roman": (
            "🌡️ **Jwaram (Fever) Vivarana & Safe Care:**\n\n"
            "• **Jwaram Ante Enti?**: Shareeram infection thoti fight chesthunappudu immune system body temperature ni penchuthundi.\n"
            "• **Safe Home Tips**:\n"
            "  - Thermometer thoti temperature check cheyyandi.\n"
            "  - Pushkalanga neellu, kobbari neellu, majjiga thagandi.\n"
            "  - Light cotton battalu vesukoni full rest theesukondi.\n"
            "• **Doctor Ni Eppudu Kalavali**:\n"
            "  - 3 days nundi jwaram thaggakapothe leda 102°F kante ekkuva unte.\n"
            "• **🚨 Emergency Alert**: Oopiri aadanappudu leda spruha thappithe ventane 112 ku call cheyyandi."
        ),
        "follow_ups": [
            "How often should I record my temperature?",
            "What should I eat when I have a fever?",
            "When does fever require emergency care?"
        ]
    },
    {
        "id": "RULE_SLEEP",
        "keywords": ["sleep", "improve my sleep", "insomnia", "cannot sleep", "bedtime", "nidra", "nidra pattatledu", "నిద్ర", "నిద్ర పట్టడం లేదు"],
        "category": "Sleep Architecture & Circadian Rest",
        "title": "Sleep Hygiene & Restorative Circadian Optimization",
        "response_en": (
            "🌙 **Clinical Strategies for Restorative Sleep:**\n\n"
            "• **Target Duration**: Healthy adults require **7 to 9 hours** of consolidated nightly sleep.\n"
            "• **Circadian Rhythm Anchoring**:\n"
            "  - Wake up at the exact same time every morning (including weekends) to anchor your master clock.\n"
            "  - Get 10–15 minutes of natural sunlight within an hour of waking.\n"
            "• **Evening Digital Wind-Down**:\n"
            "  - Stop viewing smartphones, laptops, and bright blue LED screens at least 45 minutes before sleep.\n"
            "  - Avoid heavy caffeine (tea, coffee, energy drinks) after 2:00 PM.\n"
            "• **Bedroom Optimization**:\n"
            "  - Keep your bedroom dark, quiet, and comfortably cool (around 20–22°C).\n"
            "  - Avoid heavy, spicy dinners within 2 hours of bedtime."
        ),
        "response_te": (
            "🌙 **మంచి నాణ్యమైన నిద్ర కోసం శాస్త్రీయ చిట్కాలు:**\n\n"
            "• **సమయం**: పెద్దలకు ప్రతి రాత్రి **7 నుండి 9 గంటల** నిద్ర అత్యవసరం.\n"
            "• **నిద్ర నియమాలు**:\n"
            "  - ప్రతిరోజూ ఉదయం ఒకే సమయానికి మేల్కొనడం అలవాటు చేసుకోండి.\n"
            "  - పడుకునే 45 నిమిషాల ముందు మొబైల్ మరియు టీవీ స్క్రీన్లను చూడటం ఆపండి.\n"
            "  - మధ్యాహ్నం 2 గంటల తర్వాత కాఫీ, టీలకు దూరంగా ఉండండి.\n"
            "  - పడకగదిని చీకటిగా, నిశ్శబ్దంగా మరియు చల్లగా ఉంచండి."
        ),
        "response_roman": (
            "🌙 **Manchi Nidra (Better Sleep) Kosam Tips:**\n\n"
            "• **Target Hours**: Peddalaku daily **7 to 9 hours** restful sleep chala avasaram.\n"
            "• **Important Habits**:\n"
            "  - Padukune 45 minutes mundhu mobile phones vadilesi lights dim cheyyandi.\n"
            "  - Daily oka fixed time ki padukondi mariyu lechandi.\n"
            "  - Afternoon 2 PM tharuvatha tea leda coffee thagakandi.\n"
            "  - Dinner light ga theesukondi mariyu room ni cool & dark ga unchandi."
        ),
        "follow_ups": [
            "How does screen time affect melatonin?",
            "What is the 10-3-2-1-0 sleep rule?",
            "How to log sleep in the Wellness Tracker?"
        ]
    },
    {
        "id": "RULE_WATER",
        "keywords": ["water", "water intake", "how much water", "hydration", "neellu", "neeru", "నీరు", "మంచినీరు"],
        "category": "Daily Fluid Requirements",
        "title": "Optimal Daily Hydration Science",
        "response_en": (
            "💧 **Optimal Daily Hydration Guidelines:**\n\n"
            "• **Standard Benchmark**: Most adults thrive on **2.5 to 3.5 liters (10–14 glasses)** of total fluid intake per day.\n"
            "• **Weight Rule**: Approximately **30 to 35 ml per kilogram of body weight** daily.\n"
            "• **Hydration Indicators**: Pale-straw or light-yellow urine indicates healthy hydration balance.\n"
            "• **Tips**:\n"
            "  - Start your morning with 1–2 glasses of room-temperature water.\n"
            "  - Increase intake during humid Indian weather, intense workouts, or illness."
        ),
        "response_te": (
            "💧 **రోజువారీ నీటి వినియోగ మార్గదర్శకాలు:**\n\n"
            "• **పరిమాణం**: పెద్దలు ప్రతిరోజూ **2.5 నుండి 3.5 లీటర్ల (10–14 గ్లాసులు)** నీరు లేదా ఆరోగ్యకరమైన ద్రవాలు తాగాలి.\n"
            "• **లక్షణం**: మూత్రం లేత గడ్డి రంగులో ఉండటం సరైన హైడ్రేషన్‌కు సంకేతం.\n"
            "• **చిట్కాలు**: ఉదయాన్నే లేవగానే 1-2 గ్లాసుల నీరు తాగండి; కొబ్బరి నీరు మరియు మజ్జిగ శరీరానికి చాలా మేలు చేస్తాయి."
        ),
        "response_roman": (
            "💧 **Daily Water Intake Guidelines:**\n\n"
            "• **Standard Amount**: Daily **2.5 to 3.5 liters (10-14 glasses)** neellu thagadam arogyaniki manchidi.\n"
            "• **Good Sign**: Pale yellow urine indicates proper hydration.\n"
            "• **Tips**: Morning lechinappudu 1-2 glasses water thagandi; majjiga and kobbari neellu chala help chesthayi."
        ),
        "follow_ups": [
            "What happens if you drink too much water?",
            "How to track hydration goals in HealthSaathi?",
            "Healthy hydration alternatives to plain water"
        ]
    }
]


# ==============================================================================
# OPTIONAL LOCAL LLM INTEGRATION HOOK
# ==============================================================================

def query_optional_local_llm(prompt: str, system_prompt: str) -> Optional[str]:
    """
    Checks for an optional local LLM daemon (e.g., Ollama or local OpenAI endpoint).
    Returns response text if available within a strict 500ms timeout.
    Returns None if no local LLM is running, safely falling back to rule-based engine.
    Does NOT require paid APIs, external cloud calls, or API keys.
    """
    local_url = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
    model_name = os.environ.get("LOCAL_LLM_MODEL", "llama3")

    try:
        req_data = json.dumps({
            "model": model_name,
            "prompt": f"{system_prompt}\n\nUser Inquiry: {prompt}",
            "stream": False
        }).encode("utf-8")

        req = urllib.request.Request(
            local_url,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        # Fast 0.5s timeout: will immediately fallback if local server is not active
        with urllib.request.urlopen(req, timeout=0.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response")
    except Exception:
        # Expected when no local daemon is installed; silently return None for rule-based handling
        return None


# ==============================================================================
# ASSISTANT RESPONSE DISPATCHER
# ==============================================================================

def get_assistant_response(
    query: str,
    user_id: Optional[int] = None,
    lang: Optional[str] = "en"
) -> Dict[str, Any]:
    """
    Evaluates health queries following strict clinical priority:
    1. Red-flag emergency detection (Highest priority - 112 routing)
    2. Medicine prescription requests (Non-prescriptive safety directive)
    3. Multilingual symptom and lifestyle education (English, Telugu, Roman Telugu)
    4. Optional local LLM conversational enhancement (if running locally)
    5. Fallback clarification prompts with follow-ups
    """
    clean_query = query.strip() if query else ""
    clean_lower = clean_query.lower()

    # Detect user language preference
    effective_lang = lang or "en"
    if "in telugu" in clean_lower or "telugu lo" in clean_lower or "telugulo" in clean_lower:
        effective_lang = "te"
    elif "in roman telugu" in clean_lower or "roman telugu" in clean_lower:
        effective_lang = "te-roman"
    elif re.search(r'[\u0C00-\u0C7F]', clean_query):
        effective_lang = "te"

    footer = get_disclaimer(effective_lang)

    # Empty query guard
    if not clean_query or len(clean_query) < 2:
        return {
            "category": "Clarification Guidance",
            "rule_id": "RULE_UNCLEAR_INPUT",
            "title": "Please Describe Your Symptoms",
            "content": get_text("unclear_prompt", effective_lang) + footer,
            "matched_rule": "Rule: Input Validation Guard",
            "is_emergency": False,
            "follow_ups": [
                "Naaku jwaram ga undi.",
                "I have a headache.",
                "Explain dehydration in Telugu.",
                "How can I improve my sleep?"
            ]
        }

    # ==========================================================================
    # STAGE 1: HIGH-PRIORITY EMERGENCY RED-FLAG CHECK
    # ==========================================================================
    emergency = detect_emergency(clean_query, lang=effective_lang)
    if emergency:
        content = (
            f"### {emergency['headline']}\n\n"
            f"**⚠️ Category:** {emergency['matched_category']}\n\n"
            f"{emergency['description']}\n\n"
            f"📞 **EMERGENCY HELPLINE:** `{emergency['emergency_number']}`\n\n"
            f"**Immediate Safety Actions:**\n"
            + "\n".join([f"• {act}" for act in emergency["urgent_actions"]])
            + f"\n\n---\n*{emergency['limitations']}*"
        )
        return {
            "category": "Emergency Red-Flag Detection",
            "rule_id": emergency["rule_id"],
            "title": emergency["headline"],
            "content": content,
            "matched_rule": "🚨 Critical Rule: Emergency Triage Filter (Red Flag Detected)",
            "is_emergency": True,
            "follow_ups": [
                "Call 112 Emergency Hotline",
                "Nearest Hospital Casualty steps",
                "What to inform emergency ambulance?"
            ]
        }

    # ==========================================================================
    # STAGE 2: MEDICATION SAFETY / TABLET REQUEST GUARD
    # ==========================================================================
    med_terms = ["tablet", "medicine", "pill", "syrup", "prescribe", "antibiotic", "dosage", "mandulu", "మందులు"]
    if any(m in clean_lower for m in med_terms) and any(w in clean_lower for w in ["give", "what", "suggest", "which", "recommend", "ivvandi"]):
        med_card = (
            "### 💊 Clinical Medication Safety Directive\n\n"
            "As an AI health assistant, **I do not prescribe medications or recommend specific drug dosages**.\n\n"
            "**Key Safety Reasons**:\n"
            "• Safe pharmaceutical choice requires in-person medical evaluation of kidney function, liver enzyme profile, and drug-drug interactions.\n"
            "• Over-the-counter painkillers or antibiotics can mask severe evolving pathology or cause adverse reactions.\n\n"
            "**Recommended Action**:\n"
            "• Please consult a registered medical practitioner or licensed clinical pharmacist for tailored prescription medicines."
        )
        return {
            "category": "Medication Safety Guidance",
            "rule_id": "RULE_MEDICINE_NON_PRESCRIPTIVE",
            "title": "Medication Safety Directive",
            "content": med_card + footer,
            "matched_rule": "Rule: Non-Prescriptive Clinical Safety Guard",
            "is_emergency": False,
            "follow_ups": [
                "When should I consult a doctor for medicines?",
                "Safe non-medicinal home care tips",
                "How to record my doctor-prescribed medicines?"
            ]
        }

    # ==========================================================================
    # STAGE 3: RULE-BASED CLINICAL & WELLNESS KNOWLEDGE BASE
    # ==========================================================================
    best_rule = None
    best_score = 0
    for rule in KNOWLEDGE_RULES:
        score = sum(1 for kw in rule["keywords"] if kw in clean_lower)
        if score > best_score:
            best_score = score
            best_rule = rule

    if best_rule and best_score > 0:
        if effective_lang == "te":
            text = best_rule.get("response_te", best_rule["response_en"])
        elif effective_lang == "te-roman":
            text = best_rule.get("response_roman", best_rule["response_en"])
        else:
            text = best_rule["response_en"]

        return {
            "category": best_rule["category"],
            "rule_id": best_rule["id"],
            "title": best_rule["title"],
            "content": text + footer,
            "matched_rule": f"Rule: Health Knowledge Domain [{best_rule['category']}]",
            "is_emergency": False,
            "follow_ups": best_rule.get("follow_ups", [])
        }

    # ==========================================================================
    # STAGE 4: OPTIONAL LOCAL LLM (IF AVAILABLE, ELSE SAFE FALLBACK)
    # ==========================================================================
    sys_prompt = (
        "You are HealthSaathi AI, a compassionate educational health assistant. "
        "Strictly non-diagnostic and non-prescriptive. Provide safe educational information."
    )
    llm_resp = query_optional_local_llm(clean_query, sys_prompt)
    if llm_resp:
        return {
            "category": "Conversational Intelligence",
            "rule_id": "RULE_LOCAL_LLM",
            "title": "Health Education Response",
            "content": llm_resp + footer,
            "matched_rule": "Engine: Local LLM Integration (Ollama / Local Server)",
            "is_emergency": False,
            "follow_ups": [
                "When should I see a doctor?",
                "What safe self-care steps can I take?",
                "How to track this in Wellness Tracker?"
            ]
        }

    # ==========================================================================
    # STAGE 5: CONVERSATIONAL FALLBACK & EXAMPLE PROMPTS
    # ==========================================================================
    greeting_words = ["hi", "hello", "hey", "namaste", "good morning", "good evening", "నమస్తే", "బాగున్నారా"]
    is_greeting = any(clean_lower == g or clean_lower.startswith(g + " ") for g in greeting_words)

    if is_greeting:
        reply = get_text("greeting", effective_lang)
    else:
        reply = get_text("unclear_prompt", effective_lang)

    return {
        "category": "Conversational Guidance",
        "rule_id": "RULE_GENERAL_FALLBACK",
        "title": "HealthSaathi AI Assistant",
        "content": reply + footer,
        "matched_rule": "Rule: Conversational Clarification & Suggested Prompts",
        "is_emergency": False,
        "follow_ups": [
            "Naaku jwaram ga undi.",
            "I have a headache.",
            "Explain dehydration in Telugu.",
            "How can I improve my sleep?"
        ]
    }
