"""
symptom_engine.py - Upgraded Symptom-Aware Rules Engine & Clinical Safety Triage
Provides:
1. High-priority Emergency Detection (India 112 / 108)
2. Safe, non-prescriptive Medicine Inquiry Guidance & Existing Prescription Lookup
3. Natural Language Symptom Parsing with Typo/Variation Tolerance
4. Structured 6-Point Educational Symptom Assessment
5. Intelligent Follow-up Question Generation
6. Complete English & Telugu Bilingual Support
Strictly non-diagnostic and non-prescriptive.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import database


# ==============================================================================
# 1. EMERGENCY SAFETY RULES (HIGHEST PRIORITY)
# ==============================================================================

EMERGENCY_RULES = [
    {
        "id": "EMERGENCY_CHEST_CARDIAC",
        "keywords": [
            "chest pain", "chest pressure", "heart attack", "crushing chest",
            "chest tightness", "pain radiating to arm", "left arm pain", "pain in jaw",
            "ఛాతీ నొప్పి", "గుండెపోటు", "ఛాతీలో నొప్పి", "గుండె నొప్పి",
            "gunde noppi", "chati noppi", "chaati noppi", "chathilo noppi", "gunde potu", "heart attack ga undi"
        ],
        "category": "Cardiac / Acute Chest Pain",
        "description_en": "Concerning chest pain or pressure potentially indicating acute cardiac compromise.",
        "description_te": "తీవ్రమైన ఛాతీ నొప్పి లేదా ఒత్తిడి, ఇది గుండె సంబంధిత అత్యవసర పరిస్థితిని సూచించవచ్చు.",
        "description_roman": "Teevramaina chati noppi leda gunde sambhandhita emergency paristhithi."
    },
    {
        "id": "EMERGENCY_BREATHING",
        "keywords": [
            "difficulty breathing", "severe shortness of breath", "cannot breathe", "can't breathe",
            "struggling to breathe", "gasping for air", "choking", "turning blue", "cyanosis",
            "శ్వాస తీసుకోవడంలో ఇబ్బంది", "శ్వాస ఆడటం లేదు", "ఉబ్బసం తీవ్రం",
            "oopiri aadatledu", "oopiri aadatam ledu", "swasa aadatledu", "swasa kastam", "gali aadatledu"
        ],
        "category": "Severe Respiratory Distress",
        "description_en": "Severe respiratory compromise or acute inability to breathe comfortably.",
        "description_te": "తీవ్రమైన శ్వాసకోశ సమస్య లేదా గాలి సరిగా తీసుకోలేకపోవడం.",
        "description_roman": "Teevramaina swasa samasya leda oopiri aadanappudu ventane emergency hospital ki vellali."
    },
    {
        "id": "EMERGENCY_STROKE_FAST",
        "keywords": [
            "facial drooping", "face droop", "slurred speech", "difficulty speaking", "cannot speak",
            "weakness on one side", "paralysis on one side", "numbness on one side", "stroke",
            "ముఖం వంకరపోవడం", "మాట తడబడటం", "ఒక వైపు బలహీనత", "పక్షవాతం",
            "mata thadabadatam", "mata ravatledu", "mukham vankara", "pakshavatham", "oka vaipu cheyyi laagatledu"
        ],
        "category": "Suspected Stroke (F.A.S.T.)",
        "description_en": "Signs of acute neurological deficit or stroke (facial drooping, arm weakness, speech difficulty).",
        "description_te": "తీవ్రమైన నాడీ సంబంధిత సమస్య లేదా పక్షవాత సంకేతాలు (ముఖం, చేతి బలహీనత, మాట తడబడటం).",
        "description_roman": "Pakshavatham sankethalu (mukham vankara, cheyyi balheenatha, mata thadabadatam)."
    },
    {
        "id": "EMERGENCY_UNCONSCIOUS",
        "keywords": [
            "unconscious", "loss of consciousness", "fainted with head injury", "passed out",
            "blacked out and fell", "unresponsive", "స్పృహ కోల్పోవడం", "స్పృహ తప్పి పడిపోవడం",
            "spruha thappindi", "spruha ledhu", "kallu thirigi padipoyadu", "telivi thappindi"
        ],
        "category": "Altered Consciousness / Severe Syncope",
        "description_en": "Loss of consciousness, unresponsiveness, or syncopal episode associated with trauma.",
        "description_te": "స్పృహ కోల్పోవడం లేదా తలకు గాయం తర్వాత స్పృహ తప్పడం.",
        "description_roman": "Spruha thappadam leda thalaku gaayam tharuvatha spruha kolpovadam."
    },
    {
        "id": "EMERGENCY_BLEEDING",
        "keywords": [
            "severe bleeding", "bleeding profusely", "coughing up blood", "vomiting blood",
            "blood in vomit", "hemoptysis", "రక్తం కారడం", "రక్తం వాంతి", "దగ్గులో రక్తం",
            "raktham kaaruthondi", "raktham vanthi", "daggulo raktham", "raktham paduthondi"
        ],
        "category": "Acute Hemorrhage / Significant Bleeding",
        "description_en": "Severe, uncontrolled bleeding or hemoptysis/hematemesis.",
        "description_te": "తీవ్రమైన రక్తస్రావం లేదా దగ్గు/వాంతిలో రక్తం పడటం.",
        "description_roman": "Teevramaina rakthasravam leda daggulo/vanthilo raktham padatam."
    },
    {
        "id": "EMERGENCY_ANAPHYLAXIS",
        "keywords": [
            "throat swelling", "swollen tongue", "anaphylaxis", "severe allergic reaction",
            "lips swollen and cannot breathe", "గొంతు వాపు", "తీవ్రమైన అలెర్జీ",
            "gonthu vaapu", "naluka vaachindi", "severe allergy"
        ],
        "category": "Anaphylaxis / Severe Allergy",
        "description_en": "Severe systemic allergic response with airway compromise.",
        "description_te": "శ్వాస మార్గాన్ని అడ్డుకునే తీవ్రమైన అలెర్జీ ప్రతిచర్య.",
        "description_roman": "Swasa margam addam padela teevramaina allergy prathicharya."
    },
    {
        "id": "EMERGENCY_THUNDERCLAP",
        "keywords": [
            "worst headache of my life", "sudden explosive headache", "thunderclap headache",
            "headache with stiff neck and high fever", "హఠాత్తుగా తీవ్రమైన తలనొప్పి",
            "bhayankaramaina thala noppi", "sudden tala noppi"
        ],
        "category": "Thunderclap Headache / Neurological Red Flag",
        "description_en": "Sudden onset of explosive severe headache or meningeal signs.",
        "description_te": "హఠాత్తుగా వచ్చిన భరించలేని తీవ్రమైన తలనొప్పి.",
        "description_roman": "Hathathuga vachina bharinchaleni teevramaina thala noppi."
    },
    {
        "id": "EMERGENCY_POISONING",
        "keywords": [
            "poisoning", "swallowed poison", "overdose", "drank chemical", "toxic ingestion",
            "విషం తాగడం", "ఓవర్‌డోస్",
            "visham thagadu", "mandulu ekkuva thagadu", "poison"
        ],
        "category": "Toxic Ingestion / Overdose",
        "description_en": "Suspected ingestion of toxic substances or pharmaceutical overdose.",
        "description_te": "విషపూరిత పదార్థాలు తీసుకోవడం లేదా మందుల ఓవర్‌డోస్.",
        "description_roman": "Vishapooritha padarthalu theesukovadam leda mandula overdose."
    }
]


def detect_emergency(text: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """
    Evaluates text for high-priority emergency warning signs.
    Returns emergency guidance immediately if detected.
    """
    clean_text = text.lower().strip()
    
    for rule in EMERGENCY_RULES:
        for kw in rule["keywords"]:
            if kw in clean_text:
                if lang == "te":
                    headline = "🚨 తీవ్రమైన అత్యవసర హెచ్చరిక గుర్తించబడింది!"
                    category_txt = rule["description_te"]
                    advice = [
                        "ఏదైనా శారీరక శ్రమను వెంటనే ఆపండి మరియు సురక్షితమైన స్థితిలో విశ్రాంతి తీసుకోండి.",
                        "వెంటనే 112 (భారతదేశ అత్యవసర నంబర్) లేదా 108 (అంబులెన్స్) కు కాల్ చేయండి.",
                        "స్వయంగా వాహనం నడపవద్దు; అత్యవసర సేవల ద్వారా వెంటనే సమీప ఆసుపత్రికి వెళ్లండి.",
                        "మీ అత్యవసర పరిచయం మరియు ప్రస్తుత మందుల జాబితాను సిద్ధంగా ఉంచుకోండి."
                    ]
                    limitation_note = (
                        "ముఖ్య గమనిక: అత్యవసర నియమాలు ప్రాథమిక హెచ్చరిక సంకేతాలపై ఆధారపడి ఉంటాయి. "
                        "జాబితాలో లేని లక్షణాలు ఉన్నప్పటికీ ప్రమాదం ఉండవచ్చు. మీ ఆరోగ్యం తీవ్రంగా ఉన్నట్లు అనిపిస్తే వెంటనే వైద్య సహాయం పొందండి."
                    )
                else:
                    headline = "🚨 POTENTIAL MEDICAL EMERGENCY DETECTED!"
                    category_txt = rule["description_en"]
                    advice = [
                        "Cease all physical exertion immediately and rest in a supported, comfortable position.",
                        "Call 112 (India General Emergency) or 108 (Ambulance) immediately, or have someone take you to the nearest Emergency Casualty.",
                        "Do NOT drive yourself to the hospital.",
                        "Keep your emergency contact and current medication list readily accessible."
                    ]
                    limitation_note = (
                        "Important Safety Notice: Emergency detection is based on predefined red-flag indicators. "
                        "The absence of listed warning signs does NOT guarantee medical safety. If you feel critically ill or in acute danger, seek emergency medical care immediately."
                    )

                return {
                    "is_emergency": True,
                    "rule_id": rule["id"],
                    "matched_category": rule["category"],
                    "headline": headline,
                    "description": category_txt,
                    "emergency_number": "112 (India Emergency) | 108 (Ambulance)",
                    "urgent_actions": advice,
                    "limitations": limitation_note
                }
    return None


# ==============================================================================
# 2. MEDICINE INQUIRIES & PRESCRIPTION SAFETY ENGINE
# ==============================================================================

MEDICINE_TRIGGERS = [
    "which tablet", "what tablet", "which medicine", "what medicine", "which pill",
    "what pill", "prescribe", "give me medicine", "can i take", "should i take",
    "paracetamol", "antibiotic", "painkiller", "syrup", "capsule", "dosage", "dose",
    "stop taking medicine", "can i stop my medicine", "suggest a medicine", "tablets",
    "ఏ టాబ్లెట్ వేసుకోవాలి", "ఏ మందు వాడాలి", "మందులు సూచించండి", "యాంటీబయాటిక్", "గోలీలు"
]


def handle_medicine_inquiry(query: str, user_id: Optional[int] = None, lang: str = "en") -> Optional[Dict[str, Any]]:
    """
    Handles medicine-related inquiries with strict non-prescriptive safety rules.
    If the user has existing recorded prescriptions in the database, safely summarizes them without changes.
    """
    clean_query = query.lower().strip()
    is_med_query = any(trigger in clean_query for trigger in MEDICINE_TRIGGERS)
    
    if not is_med_query:
        return None

    # Check if user has active prescriptions in DB to help with their own recorded list
    active_prescriptions = []
    if user_id:
        try:
            records = database.get_medicine_reminders(user_id, active_only=True)
            for r in records:
                active_prescriptions.append({
                    "name": r["medicine_name"],
                    "dosage": r["dosage"],
                    "timing": f"{r['time_str']} ({r['schedule_timing']})",
                    "instructions": r["instructions"] or "As directed by physician"
                })
        except Exception:
            pass

    if lang == "te":
        title = "💊 ఔషధాల భద్రత & మార్గదర్శకత్వం"
        intro = (
            "మందులు లేదా టాబ్లెట్‌లను సూచించడం అనేది వ్యక్తి యొక్క వయస్సు, ప్రస్తుత ఆరోగ్య సమస్యలు, "
            "అలెర్జీలు, ప్రస్తుతం వాడుతున్న ఇతర మందులు, గర్భధారణ స్థితి మరియు మూత్రపిండాలు/కాలేయ పనితీరుపై ఆధారపడి ఉంటుంది."
        )
        points = [
            "ఈ అసిస్టెంట్ వైద్య నిర్ధారణలను చేయదు మరియు మందులు లేదా యాంటీబయాటిక్‌లను ప్రిస్క్రిప్షన్ చేయదు.",
            "వైద్యుని అనుమతి లేకుండా యాంటీబయాటిక్స్ లేదా ప్రిస్క్రిప్షన్ మందులు తీసుకోవద్దు.",
            "మీరు ఇప్పటికే వాడుతున్న ప్రిస్క్రిప్షన్ మోతాదులను స్వతంత్రంగా ఆపవద్దు లేదా మార్చవద్దు.",
            "సరైన ఔషధం మరియు మోతాదు కోసం ఎల్లప్పుడూ అర్హత కలిగిన వైద్యుడిని లేదా ఫార్మసిస్ట్‌ను సంప్రదించండి."
        ]
        active_header = "మీరు రికార్డ్ చేసిన ప్రస్తుత మందుల షెడ్యూల్:"
    else:
        title = "💊 Medication Safety & Non-Prescriptive Guidance"
        intro = (
            "Selecting appropriate medications safely depends entirely on individual clinical factors, including "
            "your exact age, comprehensive medical history, known drug allergies, concurrent medications, pregnancy status, and organ function."
        )
        points = [
            "This health copilot does NOT invent prescriptions, recommend specific pharmaceuticals, or determine drug dosages.",
            "Never start antibiotics, strong pain relievers, or prescription-only drugs without direct physician consultation.",
            "Never stop, reduce, or alter your doctor-prescribed medications without professional approval.",
            "Consult a licensed physician or registered pharmacist for personalized medication selection and safe dosing."
        ]
        active_header = "Your Active Prescribed Medications on Record:"

    return {
        "is_medicine_query": True,
        "title": title,
        "intro": intro,
        "principles": points,
        "active_prescriptions": active_prescriptions,
        "active_header": active_header
    }


# ==============================================================================
# 3. COMPREHENSIVE SYMPTOM DEFINITIONS & NATURAL LANGUAGE PARSER
# ==============================================================================

SYMPTOM_DATABASE = [
    {
        "id": "SYMP_HEADACHE",
        "name_en": "Headache",
        "name_te": "తలనొప్పి",
        "name_roman": "Thala Noppi (Headache)",
        "keywords": [
            "headache", "head ache", "head pain", "migraine", "head throbbing",
            "headach", "hedache", "head hurt", "తల నొప్పి", "తలపోటు", "తల బరువు",
            "thala noppi", "tala noppi", "thalanopi", "talanoppi", "thala noppiga undi", "thalanoppiga undi"
        ],
        "general_causes_en": "Common general factors include tension/stress, dehydration, eye strain from digital screens, lack of sleep, sinus congestion, or viral illness.",
        "general_causes_te": "సాధారణ కారణాలలో ఒత్తిడి, శరీరంలో నీటి కొరత (డీహైడ్రేషన్), స్క్రీన్ల వల్ల కంటి అలసట, నిద్రలేమి లేదా సైనస్ సమస్యలు ఉంటాయి.",
        "general_causes_roman": "Sadharana karanalalo manasika ottidi, neeti koratha (dehydration), computer/mobile screen fatigue, leda nidralemi untayi.",
        "self_care_en": [
            "Rest in a quiet, dimly lit, well-ventilated room.",
            "Drink 1–2 glasses of water or electrolyte fluid to ensure hydration.",
            "Take screen breaks and apply a gentle cold or warm compress to forehead/neck.",
            "Practice gentle neck and shoulder stretching to relieve tension."
        ],
        "self_care_te": [
            "ప్రశాంతమైన, తక్కువ వెలుతురు ఉన్న గదిలో విశ్రాంతి తీసుకోండి.",
            "1-2 గ్లాసుల నీరు లేదా కొబ్బరి నీరు తాగి డీహైడ్రేషన్ లేకుండా చూసుకోండి.",
            "స్క్రీన్ సమయాన్ని తగ్గించి, నుదిటిపై చల్లని లేదా గోరువెచ్చని గుడ్డను ఉంచండి."
        ],
        "self_care_roman": [
            "Prashanthamaina, thakkuva veluthuru unna gadilo vishranthi theesukondi.",
            "1-2 glasses manchineellu leda kobbari neellu thagandi.",
            "Screen time thagginchi forehead pai cool compress pettandi."
        ],
        "red_flags_en": "Sudden thunderclap pain ('worst headache of life'), confusion, high fever with stiff neck, weakness, or vision loss.",
        "red_flags_te": "హఠాత్తుగా తీవ్రమైన భరించలేని నొప్పి, మెడ పట్టేయడం, అధిక జ్వరం, చూపు మందగించడం.",
        "doctor_threshold_en": "Headaches lasting > 48 hours, worsening over time, or recurring multiple times a week.",
        "doctor_threshold_te": "తలనొప్పి 48 గంటల కంటే ఎక్కువ కొనసాగితే లేదా వారానికి పలుమార్లు వస్తుంటే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_FEVER",
        "name_en": "Fever & Chills",
        "name_te": "జ్వరం & చలి",
        "name_roman": "Jwaram & Chali (Fever)",
        "keywords": [
            "fever", "fevr", "feever", "high temperature", "chills", "shivering",
            "body hot", "pyrexia", "జ్వరం", "చలి", "ఒళ్ళు కాలుతోంది",
            "jwaram", "jvaram", "jwaran", "jwaram ga undi", "naaku jwaram", "naaku jwaram ga undi",
            "jwaram vachindi", "jwaranga undi", "ollu kaaluthondi", "ollu vediga undi"
        ],
        "general_causes_en": "Fever is typically the body's natural immune response to fighting off viral or bacterial infections (e.g. seasonal flu, common cold).",
        "general_causes_te": "శరీరం వైరల్ లేదా బ్యాక్టీరియల్ ఇన్‌ఫెక్షన్లతో పోరాడుతున్నప్పుడు రోగనిరోధక ప్రతిస్పందనగా జ్వరం వస్తుంది.",
        "general_causes_roman": "Shareeram viral leda seasonal bacterial infection tho poradinappudu natural immune response ga jwaram vasthundi.",
        "self_care_en": [
            "Ensure abundant fluid intake (warm water, broths, oral rehydration salts, soups).",
            "Prioritize physical rest and wear light, breathable clothing.",
            "Use room-temperature sponge baths if feeling very uncomfortable.",
            "Monitor and record your temperature every 4–6 hours using a thermometer."
        ],
        "self_care_te": [
            "ఎక్కువగా ద్రవాలు (గోరువెచ్చని నీరు, సూప్‌లు, కొబ్బరి నీరు) తాగండి.",
            "తగినంత విశ్రాంతి తీసుకోండి మరియు తేలికపాటి దుస్తులు ధరించండి.",
            "ప్రతి 4-6 గంటలకు థర్మామీటర్‌తో ఉష్ణోగ్రతను రికార్డ్ చేయండి."
        ],
        "self_care_roman": [
            "Ekkuvaga dravamulu (goruvechani neellu, soups, kobbari neellu, ORS) thagandi.",
            "Taginantha rest theesukondi mariyu thelikapati battalu vesukondi.",
            "Prathi 4-6 hours ki thermometer tho body temperature record cheyyandi."
        ],
        "red_flags_en": "Temperature ≥ 103°F (39.4°C), difficulty breathing, persistent vomiting, stiff neck, or extreme lethargy.",
        "red_flags_te": "ఉష్ణోగ్రత 103°F కన్నా ఎక్కువ ఉండటం, శ్వాస ఆడకపోవడం, మెడ బిగుసుకుపోవడం.",
        "doctor_threshold_en": "Fever persisting more than 3 days, fever in infants/elderly, or fever not responding to basic rest.",
        "doctor_threshold_te": "జ్వరం 3 రోజుల కంటే ఎక్కువ కొనసాగితే ఖచ్చితంగా వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_COUGH",
        "name_en": "Cough",
        "name_te": "దగ్గు",
        "name_roman": "Daggu (Cough)",
        "keywords": [
            "cough", "coughing", "dry cough", "wet cough", "hacking cough", "khansi",
            "దగ్గు", "పొడి దగ్గు", "కఫం దగ్గు",
            "daggu", "dagguga undi", "daggutunnanu", "podi daggu", "daggutunna"
        ],
        "general_causes_en": "Cough often stems from upper airway viral infections, post-nasal drip, environmental allergens, dust exposure, or seasonal irritation.",
        "general_causes_te": "శ్వాస మార్గంలో వైరల్ ఇన్‌ఫెక్షన్లు, అలెర్జీలు, ధూళి లేదా వాతావరణ మార్పుల వల్ల సాధారణంగా దగ్గు వస్తుంది.",
        "self_care_en": [
            "Sip warm water, herbal teas, or warm water with honey (for adults and children > 1 yr).",
            "Use steam inhalation (5–10 mins) to moisten irritated respiratory passages.",
            "Avoid cold drinks, smoking, and dusty/polluted air environments."
        ],
        "self_care_te": [
            "గోరువెచ్చని నీరు లేదా తేనెతో కూడిన గోరువెచ్చని నీరు తాగండి.",
            "రోజుకు రెండుసార్లు ఆవిరి పట్టండి.",
            "చల్లని పానీయాలు మరియు దుమ్ముకు దూరంగా ఉండండి."
        ],
        "red_flags_en": "Shortness of breath, coughing up blood, wheezing, or chest pain while breathing.",
        "red_flags_te": "దగ్గులో రక్తం పడటం, తీవ్రమైన ఆయాసం లేదా శ్వాస తీసుకునేటప్పుడు ఛాతీ నొప్పి.",
        "doctor_threshold_en": "Cough lasting longer than 2–3 weeks, thick discolored phlegm, or unexplained weight loss.",
        "doctor_threshold_te": "దగ్గు 2-3 వారాల కంటే ఎక్కువ కొనసాగితే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_SORE_THROAT",
        "name_en": "Sore Throat",
        "name_te": "గొంతు నొప్పి",
        "keywords": [
            "sore throat", "throat pain", "throat irritation", "scratchy throat",
            "difficulty swallowing", "గొంతు నొప్పి", "గొంతు మంట"
        ],
        "general_causes_en": "Often caused by viral pharyngitis, cold viruses, vocal strain, or dry indoor air.",
        "general_causes_te": "వైరల్ ఇన్‌ఫెక్షన్లు, జలుబు, గట్టిగా అరవడం లేదా పొడి గాలి వల్ల గొంతు నొప్పి వస్తుంది.",
        "self_care_en": [
            "Gargle with warm salt water (1/2 tsp salt in 1 glass warm water) 3–4 times daily.",
            "Stay well hydrated with warm liquids like herbal decoctions or soups.",
            "Rest your vocal cords and avoid spicy, acidic foods that irritate the throat."
        ],
        "self_care_te": [
            "గోరువెచ్చని ఉప్పు నీటితో రోజుకు 3-4 సార్లు పుక్కిలించండి.",
            "గోరువెచ్చని సూప్‌లు తాగండి, కారమైన ఆహారాన్ని నివారించండి."
        ],
        "red_flags_en": "Inability to swallow saliva, difficulty opening the mouth, or breathing difficulty.",
        "red_flags_te": "లాలాజలాన్ని కూడా మింగలేకపోవడం లేదా నోరు తెరవడంలో తీవ్ర ఇబ్బంది.",
        "doctor_threshold_en": "Severe throat pain lasting > 5 days or accompanied by high fever without cold symptoms.",
        "doctor_threshold_te": "గొంతు నొప్పి 5 రోజుల కంటే ఎక్కువ కొనసాగితే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_COLD_RUNNY_NOSE",
        "name_en": "Runny Nose & Cold",
        "name_te": "జలుబు & ముక్కు కారడం",
        "keywords": [
            "runny nose", "cold", "sneezing", "stuffy nose", "nasal congestion",
            "blocked nose", "జలుబు", "ముక్కు కారడం", "ముక్కు దిబ్బడ"
        ],
        "general_causes_en": "Upper respiratory viral illness (rhinovirus) or environmental allergic rhinitis.",
        "general_causes_te": "సాధారణంగా రైనోవైరస్ వల్ల వచ్చే జలుబు లేదా వాతావరణ అలెర్జీలు కారణం.",
        "self_care_en": [
            "Warm steam inhalation to relieve congestion.",
            "Saline nasal spray/drops to clear nasal passages naturally.",
            "Adequate sleep and warm hydration."
        ],
        "self_care_te": [
            "ఆవిరి పట్టడం ద్వారా ముక్కు దిబ్బడను తగ్గించుకోండి.",
            "సెలైన్ నేసల్ స్ప్రే వాడటం మరియు పుష్కలంగా నీరు తాగడం."
        ],
        "red_flags_en": "Facial swelling, high fever, or intense sinus pain around eyes/forehead.",
        "red_flags_te": "కళ్ళ చుట్టూ తీవ్రమైన నొప్పి, ముఖం వాపు లేదా అధిక జ్వరం.",
        "doctor_threshold_en": "Symptoms not resolving after 10 days or worsening after initial improvement.",
        "doctor_threshold_te": "10 రోజుల తర్వాత కూడా జలుబు తగ్గకపోతే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_STOMACH_PAIN",
        "name_en": "Stomach Pain / Indigestion",
        "name_te": "కడుపు నొప్పి & అజీర్ణం",
        "keywords": [
            "stomach pain", "stomach ache", "abdominal pain", "tummy ache", "belly pain",
            "gastric", "acidity", "indigestion", "heartburn", "cramps", "కడుపు నొప్పి", "కడుపు మంట", "అజీర్ణం"
        ],
        "general_causes_en": "Common factors include dietary indigestion, gas buildup, hyperacidity, mild gastroenteritis, or eating spicy/unaccustomed foods.",
        "general_causes_te": "అజీర్ణం, గ్యాస్, ఎసిడిటీ లేదా మసాలా ఆహారం తినడం వల్ల కడుపు నొప్పి రావచ్చు.",
        "self_care_en": [
            "Consume light, bland meals (e.g. rice porridge, bananas, curd/buttermilk).",
            "Avoid oily, deep-fried, spicy foods, carbonated beverages, and caffeine.",
            "Sip warm water or ginger/mint tea; refrain from lying flat immediately after eating."
        ],
        "self_care_te": [
            "తేలికపాటి ఆహారం (మజ్జిగ, అరటిపండు, కిచిడీ) తీసుకోండి.",
            "నూనె, మసాలా, వేపుళ్ళు మరియు శీతల పానీయాలకు దూరంగా ఉండండి."
        ],
        "red_flags_en": "Sudden severe localized pain (especially lower right abdomen), vomiting blood, black stools, or rigid abdomen.",
        "red_flags_te": "తీవ్రమైన భరించలేని కడుపు నొప్పి, వాంతిలో రక్తం లేదా నల్లటి మలం.",
        "doctor_threshold_en": "Pain persisting > 24–48 hours, high fever, or inability to keep liquids down.",
        "doctor_threshold_te": "కడుపు నొప్పి 24 గంటలకు మించి ఉంటే లేదా వాంతులు ఆగకపోతే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_DIZZINESS_WEAKNESS",
        "name_en": "Dizziness & Weakness",
        "name_te": "కళ్ళు తిరగడం & బలహీనత",
        "keywords": [
            "dizzy", "dizziness", "lightheaded", "weak", "weakness", "faint feeling",
            "vertigo", "fatigued and weak", "కళ్ళు తిరగడం", "నీరసం", "బలహీనత"
        ],
        "general_causes_en": "Dehydration, low blood sugar (missed meals), postural hypotension (standing up too quickly), fatigue, or inner ear imbalance.",
        "general_causes_te": "శరీరంలో నీరు తగ్గడం, రక్తంలో చక్కెర తగ్గడం (ఆహారం తినకపోవడం), లేదా అలసట వల్ల కళ్ళు తిరగవచ్చు.",
        "self_care_en": [
            "Sit or lie down immediately to prevent falls.",
            "Drink an oral rehydration solution (ORS), lemon water with salt and sugar, or fruit juice.",
            "Stand up slowly in stages (sit first, then stand).",
            "Rest in a cool, well-ventilated space."
        ],
        "self_care_te": [
            "కళ్ళు తిరిగినప్పుడు వెంటనే కూర్చోండి లేదా పడుకోండి.",
            "ఓఆర్ఎస్ (ORS), నిమ్మరసం లేదా పండ్ల రసం తాగండి.",
            "పడుకున్న స్థితి నుండి ఒక్కసారిగా లేవవద్దు."
        ],
        "red_flags_en": "Dizziness with chest pain, palpitations, slurred speech, one-sided weakness, or loss of consciousness.",
        "red_flags_te": "ఛాతీ నొప్పి, మాట తడబడటం లేదా స్పృహ తప్పడంతో పాటు కళ్ళు తిరగడం.",
        "doctor_threshold_en": "Frequent or recurring dizziness episodes, or dizziness not resolving with rest and fluids.",
        "doctor_threshold_te": "కళ్ళు తిరగడం పదే పదే వస్తుంటే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_SLEEP_PROBLEMS",
        "name_en": "Sleep Problems / Insomnia",
        "name_te": "నిద్రలేమి & నిద్ర సమస్యలు",
        "keywords": [
            "trouble sleeping", "insomnia", "cannot sleep", "can't sleep", "sleep problem",
            "sleepless", "broken sleep", "waking up", "నిద్రలేమి", "నిద్ర పట్టడం లేదు"
        ],
        "general_causes_en": "Elevated mental stress, late-evening screen time, irregular schedule, excessive caffeine, or noisy sleeping environment.",
        "general_causes_te": "మానసిక ఒత్తిడి, రాత్రిపూట మొబైల్ వాడకం, కెఫీన్ లేదా అనవసరపు శబ్దాలు నిద్రను భంగపరుస్తాయి.",
        "self_care_en": [
            "Maintain a strict, fixed bedtime and wake-up time every day.",
            "Turn off screens (phones, laptops, TV) 45–60 minutes before bed.",
            "Keep the bedroom cool, dark, and quiet.",
            "Avoid caffeine or heavy meals after 3:00 PM; try 4-7-8 breathing relaxation."
        ],
        "self_care_te": [
            "ప్రతిరోజూ ఒకే సమయానికి పడుకోవడం మరియు మేల్కొనడం అలవాటు చేసుకోండి.",
            "పడుకునే గంట ముందు మొబైల్ మరియు టీవీ స్క్రీన్లను ఆపివేయండి.",
            "రాత్రిపూట కాఫీ, టీలకు దూరంగా ఉండండి."
        ],
        "red_flags_en": "Chronic daytime falling asleep while driving, loud gasping/choking at night (sleep apnea), or severe depression.",
        "red_flags_te": "డ్రైవింగ్ సమయంలో నిద్రపోవడం లేదా రాత్రి శ్వాస ఆగిపోతున్నట్లు అనిపించడం.",
        "doctor_threshold_en": "Sleep disturbances persisting > 3–4 weeks significantly impairing daytime cognitive functioning.",
        "doctor_threshold_te": "నిద్రలేమి 3-4 వారాల కంటే ఎక్కువ కొనసాగితే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_BODY_PAIN_FATIGUE",
        "name_en": "Body Pain & Fatigue",
        "name_te": "ఒళ్ళు నొప్పులు & అలసట",
        "keywords": [
            "body pain", "body ache", "fatigue", "tiredness", "exhaustion",
            "muscle ache", "muscle pain", "lethargic", "ఒళ్ళు నొప్పులు", "అలసట", "శరీర నొప్పులు"
        ],
        "general_causes_en": "Viral prodrome, physical overexertion, sleep deprivation, dehydration, or prolonged poor posture.",
        "general_causes_te": "వైరల్ ఇన్‌ఫెక్షన్ ప్రారంభ దశ, శారీరక శ్రమ, నిద్రలేమి లేదా అలసట వల్ల ఒళ్ళు నొప్పులు వస్తాయి.",
        "self_care_en": [
            "Rest your muscles and prioritize 7–8 hours of sound sleep.",
            "Take a warm bath or apply warm compress to aching muscles.",
            "Maintain balanced hydration and wholesome nutrition (protein, leafy greens).",
            "Perform light, non-strenuous stretching."
        ],
        "self_care_te": [
            "శరీరానికి తగినంత విశ్రాంతినివ్వండి మరియు 7-8 గంటలు నిద్రపోండి.",
            "గోరువెచ్చని నీటితో స్నానం చేయండి.",
            "పౌష్టికాహారం మరియు తగినంత నీరు తీసుకోండి."
        ],
        "red_flags_en": "Severe muscle swelling, inability to move limbs, dark cola-colored urine, or accompanied by high fever.",
        "red_flags_te": "కాళ్ళు చేతులు కదపలేకపోవడం లేదా మూత్రం ముదురు రంగులో రావడం.",
        "doctor_threshold_en": "Fatigue or body aches persisting beyond 1–2 weeks without clear explanation.",
        "doctor_threshold_te": "నొప్పులు మరియు అలసట 2 వారాల కంటే ఎక్కువ కొనసాగితే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_NAUSEA_VOMITING",
        "name_en": "Nausea & Vomiting",
        "name_te": "వాంతులు & వికారం",
        "keywords": [
            "nausea", "nauseous", "vomit", "vomiting", "throwing up", "queasy",
            "sick to my stomach", "వాంతులు", "వికారం"
        ],
        "general_causes_en": "Food intolerance, mild gastroenteritis, motion sickness, acidity, or viral stomach infection.",
        "general_causes_te": "కలుషిత ఆహారం, ఎసిడిటీ, ప్రయాణ అలసట లేదా వైరల్ ఇన్‌ఫెక్షన్ వల్ల వికారం/వాంతులు రావచ్చు.",
        "self_care_en": [
            "Take small, frequent sips of Oral Rehydration Solution (ORS), coconut water, or clear broth.",
            "Avoid solid foods until nausea subsides; then restart with bland crackers or toast.",
            "Avoid dairy, greasy, and sweet foods."
        ],
        "self_care_te": [
            "కొద్దికొద్దిగా ఓఆర్ఎస్ (ORS) నీరు లేదా కొబ్బరి నీరు తాగండి.",
            "నూనె, పాలు మరియు తీపి పదార్థాలకు దూరంగా ఉండండి."
        ],
        "red_flags_en": "Inability to keep liquids down for > 24 hours, blood in vomit, extreme lethargy, or signs of severe dehydration.",
        "red_flags_te": "24 గంటలకు పైగా నీరు కూడా తాగలేకపోవడం లేదా వాంతిలో రక్తం పడటం.",
        "doctor_threshold_en": "Vomiting persisting more than 24 hours in adults or 12 hours in young children.",
        "doctor_threshold_te": "వాంతులు 24 గంటలకు మించి కొనసాగితే వెంటనే వైద్యుడిని సంప్రదించండి."
    },
    {
        "id": "SYMP_DIARRHEA",
        "name_en": "Diarrhea / Loose Stools",
        "name_te": "విరేచనాలు",
        "keywords": [
            "diarrhea", "diarrhoea", "loose motion", "loose motions", "loose stools",
            "watery stool", "విరేచనాలు", "మోషన్స్"
        ],
        "general_causes_en": "Viral gastroenteritis, foodborne illness, dietary change, or emotional stress.",
        "general_causes_te": "కలుషిత నీరు/ఆహారం లేదా కడుపులో ఇన్‌ఫెక్షన్ వల్ల విరేచనాలు రావచ్చు.",
        "self_care_en": [
            "Prevent dehydration using Oral Rehydration Salts (ORS) solution after every loose stool.",
            "Eat light, easily digestible foods like curd rice, bananas, and boiled potatoes.",
            "Avoid caffeinated drinks, alcohol, artificial sweeteners, and fried foods."
        ],
        "self_care_te": [
            "ప్రతి విరేచనం తర్వాత ఓఆర్ఎస్ (ORS) ద్రావణం తప్పనిసరిగా తాగండి.",
            "పెరుగు అన్నం, అరటిపండు వంటి తేలికపాటి ఆహారం తినండి."
        ],
        "red_flags_en": "Blood or mucus in stools, high fever, severe dizziness, or dry mouth and sunken eyes (severe dehydration).",
        "red_flags_te": "మలంలో రక్తం, తీవ్రమైన కళ్ళు తిరగడం లేదా నోరు ఎండిపోవడం.",
        "doctor_threshold_en": "Diarrhea lasting > 48 hours or occurring more than 6 times in 24 hours.",
        "doctor_threshold_te": "విరేచనాలు 2 రోజుల కంటే ఎక్కువ కొనసాగితే వైద్యుడిని సంప్రదించండి."
    }
]


# ==============================================================================
# 4. NATURAL LANGUAGE SYMPTOM EXTRACTION
# ==============================================================================

def extract_symptoms_and_context(query: str) -> Dict[str, Any]:
    """
    Parses natural language query to identify symptoms, duration cues,
    severity cues, and age indicators.
    """
    clean_q = query.lower().strip()
    
    # 1. Identify matching symptoms
    matched_symptoms = []
    for s_def in SYMPTOM_DATABASE:
        for kw in s_def["keywords"]:
            if kw in clean_q:
                matched_symptoms.append(s_def)
                break  # avoid duplicate match for same symptom definition

    # 2. Extract Duration Cues
    duration_cues = []
    duration_patterns = [
        r"(for\s+\d+\s+(?:days?|hours?|weeks?|months?))",
        r"(since\s+\w+)",
        r"(past\s+\d+\s+(?:days?|hours?|weeks?))",
        r"(last\s+\d+\s+(?:days?|hours?))",
        r"(today|yesterday|this morning|last night|few days|a week)"
    ]
    for pat in duration_patterns:
        match = re.search(pat, clean_q)
        if match:
            duration_cues.append(match.group(1))

    # 3. Extract Severity Cues
    severity_level = None
    if any(w in clean_q for w in ["severe", "unbearable", "extremely bad", "very bad", "intense", "high", "తీవ్రమైన"]):
        severity_level = "Severe"
    elif any(w in clean_q for w in ["moderate", "medium", "somewhat", "quite", "మితమైన"]):
        severity_level = "Moderate"
    elif any(w in clean_q for w in ["mild", "slight", "little", "minor", "బిడ్డ", "తేలికపాటి"]):
        severity_level = "Mild"

    # 4. Extract Age / Demographics Cues
    age_cue = None
    age_match = re.search(r"(\d{1,3})\s*(?:years?\s*old|yo|yr)", clean_q)
    if age_match:
        age_cue = f"{age_match.group(1)} years old"
    elif any(w in clean_q for w in ["child", "kid", "baby", "infant", "toddler", "పిల్లలు"]):
        age_cue = "Child / Minor"
    elif any(w in clean_q for w in ["elderly", "senior", "grandparent", "వృద్ధులు"]):
        age_cue = "Elderly / Senior"

    return {
        "matched_symptoms": matched_symptoms,
        "duration": ", ".join(duration_cues) if duration_cues else None,
        "severity": severity_level,
        "age_cue": age_cue
    }


# ==============================================================================
# 5. STRUCTURED EDUCATIONAL ASSESSMENT GENERATOR
# ==============================================================================

def generate_symptom_assessment(
    symptoms: List[Dict[str, Any]],
    duration: Optional[str] = None,
    severity: Optional[str] = None,
    age_cue: Optional[str] = None,
    user_id: Optional[int] = None,
    lang: str = "en"
) -> Dict[str, Any]:
    """
    Generates a structured, transparent 6-part health guidance assessment.
    Strictly non-diagnostic and non-prescriptive.
    """
    symptom_names_en = [s["name_en"] for s in symptoms]
    symptom_names_te = [s["name_te"] for s in symptoms]

    # Incorporate user profile context if available
    profile_context = ""
    if user_id:
        try:
            prof = database.get_profile(user_id)
            if prof:
                parts = []
                if prof["age"]:
                    parts.append(f"Age: {prof['age']} yrs")
                if prof["allergies"] and prof["allergies"] != "None":
                    parts.append(f"Known allergies: {prof['allergies']}")
                if prof["chronic_conditions"] and prof["chronic_conditions"] != "None":
                    parts.append(f"Underlying conditions: {prof['chronic_conditions']}")
                if parts:
                    profile_context = f" (Profile on record: {', '.join(parts)})"
        except Exception:
            pass

    # Follow-up questions logic
    follow_ups = []
    if not duration:
        if lang == "te":
            follow_ups.append("ఈ లక్షణాలు ఎంతకాలంగా ఉన్నాయి (కొన్ని గంటలు, 1-2 రోజులు లేదా వారం)?")
        else:
            follow_ups.append("How long have you had these symptoms (a few hours, 1–2 days, or longer)?")
    if not severity:
        if lang == "te":
            follow_ups.append("లక్షణాల తీవ్రత ఎలా ఉంది (తేలికపాటిదా, మితమైనదా లేదా రోజువారీ పనులకు ఆటంకం కలిగిస్తుందా)?")
        else:
            follow_ups.append("What is the intensity level (mild, moderate, or severely interfering with activities)?")
    if not age_cue and not profile_context:
        if lang == "te":
            follow_ups.append("లక్షణాలు ఎదుర్కొంటున్న వారి వయస్సు మరియు ఇతర ఆరోగ్య పరిస్థితులు ఏమైనా ఉన్నాయా?")
        else:
            follow_ups.append("Who is experiencing these symptoms (adult, child, senior), and are there any chronic conditions?")

    # Compile combined general causes & self-care
    if lang == "te":
        causes_list = [f"• **{s['name_te']}**: {s['general_causes_te']}" for s in symptoms]
        self_care_list = []
        for s in symptoms:
            for item in s["self_care_te"]:
                if item not in self_care_list:
                    self_care_list.append(f"• {item}")
        red_flags_list = [f"• **{s['name_te']}**: {s['red_flags_te']}" for s in symptoms]
        doctor_threshold_list = [f"• **{s['name_te']}**: {s['doctor_threshold_te']}" for s in symptoms]

        # Structured response text
        rep_symp_str = ", ".join(symptom_names_te)
        dur_str = duration if duration else "పేర్కొనబడలేదు"
        sev_str = severity if severity else "పేర్కొనబడలేదు"

        response_md = (
            f"### 📋 ఆరోగ్య లక్షణాల విశ్లేషణ & మార్గదర్శకత్వం\n\n"
            f"**1. మీరు నివేదించిన లక్షణాలు:**\n"
            f"• లక్షణాలు: **{rep_symp_str}**\n"
            f"• సమయం: {dur_str} | తీవ్రత: {sev_str}{profile_context}\n\n"
            f"**2. సాధారణ విద్యా సమాచారం & సాధ్యమైన కారణాలు:**\n"
            + "\n".join(causes_list) + "\n\n"
            f"*(గమనిక: ఇవి సాధారణ విద్యా సమాచారం మాత్రమే; ఖచ్చితమైన రోగ నిర్ధారణ కాదు.)*\n\n"
            f"**3. సురక్షితమైన స్వీయ సంరక్షణ చర్యలు:**\n"
            + "\n".join(self_care_list) + "\n\n"
            f"**4. వైద్యుడిని ఎప్పుడు సంప్రదించాలి:**\n"
            + "\n".join(doctor_threshold_list) + "\n\n"
            f"**5. గమనించవలసిన అత్యవసర హెచ్చరిక సంకేతాలు:**\n"
            + "\n".join(red_flags_list) + "\n"
            f"🚨 *ఈ అత్యవసర సంకేతాలు కనిపిస్తే వెంటనే **112** లేదా **108** కు కాల్ చేయండి.*\n\n"
            f"**6. ఔషధాల భద్రతా గమనిక:**\n"
            f"• వ్యక్తిగత వైద్యుల సలహా లేకుండా కొత్త మందులు లేదా యాంటీబయాటిక్స్ తీసుకోవద్దు.\n"
            f"• సరైన మందుల ఎంపిక కోసం ఎల్లప్పుడూ వైద్యుడిని లేదా ఫార్మసిస్ట్‌ను సంప్రదించండి."
        )

        if follow_ups:
            response_md += "\n\n---\n**మరింత స్పష్టత కోసం పరిగణించవలసిన ప్రశ్నలు:**\n" + "\n".join([f"❓ {q}" for q in follow_ups])

    else:
        causes_list = [f"• **{s['name_en']}**: {s['general_causes_en']}" for s in symptoms]
        self_care_list = []
        for s in symptoms:
            for item in s["self_care_en"]:
                if item not in self_care_list:
                    self_care_list.append(f"• {item}")
        red_flags_list = [f"• **{s['name_en']}**: {s['red_flags_en']}" for s in symptoms]
        doctor_threshold_list = [f"• **{s['name_en']}**: {s['doctor_threshold_en']}" for s in symptoms]

        rep_symp_str = ", ".join(symptom_names_en)
        dur_str = duration if duration else "Not specified"
        sev_str = severity if severity else "Not specified"

        response_md = (
            f"### 📋 Structured Symptom Education & Guidance\n\n"
            f"**1. Reported Symptoms:**\n"
            f"• Symptoms: **{rep_symp_str}**\n"
            f"• Duration: {dur_str} | Severity: {sev_str}{profile_context}\n\n"
            f"**2. General Educational Information & Potential Causes:**\n"
            + "\n".join(causes_list) + "\n\n"
            f"*(Notice: These are common educational possibilities, NOT a clinical diagnosis.)*\n\n"
            f"**3. Safe Next Steps & Home Self-Care:**\n"
            + "\n".join(self_care_list) + "\n\n"
            f"**4. When to Contact a Healthcare Professional:**\n"
            + "\n".join(doctor_threshold_list) + "\n\n"
            f"**5. Emergency Warning Signs to Watch For:**\n"
            + "\n".join(red_flags_list) + "\n"
            f"🚨 *If any of these emergency signs develop, seek emergency care immediately (Call **112** / **108** in India).*\n\n"
            f"**6. Medication Safety Note:**\n"
            f"• Do not self-prescribe medications or antibiotics based solely on symptoms.\n"
            f"• Selecting medicines safely requires evaluating your individual age, allergies, and organ function with a doctor or pharmacist."
        )

        if follow_ups:
            response_md += "\n\n---\n**Helpful Follow-Up Questions to Consider:**\n" + "\n".join([f"❓ {q}" for q in follow_ups])

    return {
        "is_symptom_assessment": True,
        "symptoms": symptom_names_en,
        "content": response_md,
        "follow_ups": follow_ups
    }


# ==============================================================================
# 6. UNCLEAR / AMBIGUOUS QUERY HANDLER
# ==============================================================================

GREETING_WORDS = ["hi", "hello", "hey", "namaste", "good morning", "good evening", "how are you", "బాగున్నారా", "నమస్తే"]


def handle_unclear_or_greeting(query: str, lang: str = "en") -> Dict[str, Any]:
    """
    Handles conversational greetings, empty queries, or ambiguous messages
    with helpful clarification and example prompts.
    """
    clean_q = query.lower().strip()

    # Greetings
    if any(clean_q == g or clean_q.startswith(g + " ") for g in GREETING_WORDS):
        if lang == "te":
            text = (
                "👋 **నమస్కారం! మీ వ్యక్తిగత ఆరోగ్య సహాయకుడికి స్వాగతం.**\n\n"
                "మీరు మీ ఆరోగ్య లక్షణాలు (ఉదా: *'నాకు తలనొప్పిగా ఉంది'*, *'జ్వరం మరియు గొంతు నొప్పి'*) "
                "లేదా వెల్‌నెస్ ప్రశ్నలను ఇక్కడ టైప్ చేయవచ్చు.\n\n"
                "నేను మీకు సురక్షితమైన విద్యా సమాచారం, స్వీయ సంరక్షణ సూచనలు మరియు అత్యవసర మార్గదర్శకత్వాన్ని అందిస్తాను."
            )
        else:
            text = (
                "👋 **Hello! Welcome to your Personal Health & Symptom Assistant.**\n\n"
                "You can describe your symptoms in natural language (e.g., *'I have a headache'*, *'I have a fever and sore throat'*), "
                "or ask wellness education questions.\n\n"
                "I will provide structured health education, safe self-care guidance, and safety triage without diagnosing or prescribing."
            )
        return {
            "type": "greeting",
            "content": text
        }

    # Empty or unclear
    if not clean_q or len(clean_q) < 3:
        if lang == "te":
            text = (
                "❓ **దయచేసి మీ లక్షణాలను కొద్దిగా వివరంగా తెలియజేయండి.**\n\n"
                "సహాయకరమైన మార్గదర్శకత్వం పొందడానికి, దయచేసి క్రింది వివరాలను పేర్కొనండి:\n"
                "1. ప్రధాన లక్షణం (ఉదా: తలనొప్పి, దగ్గు, కడుపు నొప్పి)\n"
                "2. ఎంతకాలంగా ఉంది (ఉదా: 2 రోజులు, నిన్నటి నుండి)\n"
                "3. తీవ్రత (తేలికపాటి, మితమైన, తీవ్రమైన)\n\n"
                "ఉదాహరణ: *'నాకు 2 రోజుల నుండి జ్వరం మరియు గొంతు నొప్పి ఉంది.'*"
            )
        else:
            text = (
                "❓ **I couldn't clearly identify specific symptoms or wellness topics in your message.**\n\n"
                "To provide helpful health education, please try describing:\n"
                "1. **Primary symptom** (e.g., *headache*, *fever*, *cough*, *stomach pain*)\n"
                "2. **Duration** (e.g., *for 2 days*, *since yesterday*)\n"
                "3. **Severity** (*mild*, *moderate*, or *severe*)\n\n"
                "Example: *'I have a fever and a sore throat since yesterday.'* or *'I have trouble sleeping.'*"
            )
        return {
            "type": "unclear",
            "content": text
        }

    # Unrecognized topic fallback
    if lang == "te":
        text = (
            "ℹ️ **మీరు పేర్కొన్న అంశంపై నిర్దిష్ట లక్షణాలు గుర్తించబడలేదు.**\n\n"
            "దయచేసి మీ లక్షణాలను స్పష్టంగా వివరించండి (ఉదా: *'నాకు తలనొప్పి ఉంది'*, *'కడుపు నొప్పి మరియు వికారం'*), "
            "లేదా జీవనశైలి ప్రశ్నను అడగండి (ఉదా: *'సాధారణ రక్తపోటు ఎంత?'*)."
        )
    else:
        text = (
            "ℹ️ **I couldn't match your inquiry to a specific symptom or wellness guideline.**\n\n"
            "Please try rephrasing with specific symptoms (e.g., *'I feel dizzy and weak'*, *'I have stomach pain'*) "
            "or wellness questions (e.g., *'How much water should I drink?'*, *'Tips for better sleep'*).\n\n"
            "*(If you are experiencing an acute medical emergency, please call **112** immediately.)*"
        )
    return {
        "type": "unclear",
        "content": text
    }


# ==============================================================================
# 5. THREE-TIER EMERGENCY TRIAGE SYSTEM (SAFETY PRIORITIZED)
# ==============================================================================

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
    Evaluates reported health condition across three clinical urgency tiers:
    1. 'Emergency care now' (Severe breathing difficulty, stroke warning signs, unconsciousness, chest pain, severe bleeding -> India 112)
    2. 'Prompt medical consultation' (Concerning, persistent, or worsening symptoms requiring timely evaluation)
    3. 'General self-care guidance' (Low-risk, self-care routines without detected red flags)

    Safety Constraints:
    - Strictly non-diagnostic: Explains risks and next steps, never names a disease.
    - Lack of detected keywords is NEVER treated as proof of safety.
    - Emergency instructions are never delayed.
    """
    combined_text = (text_input + " " + " ".join(symptoms)).lower()

    # --- TIER 1: EMERGENCY CARE NOW CHECK ---
    emergency_match = detect_emergency(combined_text, lang=lang)
    
    # Also check if any selected symptoms contain critical red flags
    red_flag_triggers = [
        "severe chest pain", "difficulty breathing", "cannot breathe", "stroke", 
        "slurred speech", "unconscious", "loss of consciousness", "coughing up blood",
        "severe bleeding", "poisoning", "swelling of tongue", "worst headache"
    ]
    has_red_flag = any(rf in combined_text for rf in red_flag_triggers)

    if emergency_match or has_red_flag:
        category_name = emergency_match["matched_category"] if emergency_match else "Acute Red-Flag Symptom"
        reasons = [emergency_match["description"]] if emergency_match else ["Severe physiological red flag reported requiring emergency evaluation."]
        
        return {
            "tier": "Emergency care now",
            "tier_level": 1,
            "badge_color": "rose",
            "headline": "🚨 EMERGENCY CARE NOW (DO NOT WAIT)",
            "call_to_action": "Call 112 (India Emergency) or 108 (Ambulance) IMMEDIATELY.",
            "emergency_numbers": ["112 (India General Emergency)", "108 (Free Emergency Ambulance)"],
            "category": category_name,
            "reasons": reasons,
            "urgent_actions": [
                "Stop all physical exertion immediately. Sit or lie down in a safe, supported position.",
                "Call 112 or 108 immediately, or have an accompanying person take you to the nearest Emergency Casualty.",
                "Do NOT drive yourself to the hospital.",
                "Do NOT delay emergency care to ask further questions or wait for online responses.",
                "Keep emergency contact details and your current medication list accessible."
            ],
            "limitation": "Safety Warning: This system detects pre-configured high-priority warning signs. The absence of detected keywords does NOT prove safety. If you feel in acute danger, proceed immediately to an emergency department."
        }

    # --- TIER 2: PROMPT MEDICAL CONSULTATION CHECK ---
    # Triggered by:
    # 1. High severity reported
    # 2. Symptoms lasting > 3 days (4-7 days, > 1 week, > 2 weeks)
    # 3. Multiple concurrent symptoms (≥ 3 symptoms)
    # 4. Concerning keywords (fever > 3 days, continuous vomiting, abdominal cramping, dizzy spells)
    is_persistent = duration in ["4 to 7 days", "More than 1 week", "More than 2 weeks", "More than a week"]
    is_severe_intensity = "severe" in severity.lower()
    has_multiple_symptoms = len(symptoms) >= 3
    concerning_terms = ["fever", "vomit", "dizzy", "pain", "rash", "weight loss", "stomach", "cough"]
    matches_concerning = sum(1 for term in concerning_terms if term in combined_text) >= 2

    if is_severe_intensity or is_persistent or has_multiple_symptoms or matches_concerning:
        reasons_list = []
        if is_severe_intensity:
            reasons_list.append("Reported symptom intensity is severe, affecting daily activities.")
        if is_persistent:
            reasons_list.append(f"Symptoms have persisted for {duration}, which warrants clinical investigation.")
        if has_multiple_symptoms:
            reasons_list.append(f"Multiple co-occurring symptoms reported ({', '.join(symptoms[:3])}).")
        if not reasons_list:
            reasons_list.append("Reported symptoms require timely clinical evaluation by a medical doctor.")

        return {
            "tier": "Prompt medical consultation",
            "tier_level": 2,
            "badge_color": "amber",
            "headline": "⚠️ PROMPT MEDICAL CONSULTATION RECOMMENDED",
            "call_to_action": "Schedule an appointment with a General Physician or specialist within 24 to 48 hours.",
            "emergency_numbers": ["112 (Emergency Hotline)"],
            "category": "Persistent / Worsening Health Concerns",
            "reasons": reasons_list,
            "urgent_actions": [
                "Book an appointment with a licensed healthcare practitioner or clinic for direct examination.",
                "Keep a written log of symptom progression, temperature readings, and time of onset.",
                "Stay rested and maintain gentle hydration; avoid unprescribed over-the-counter pharmaceuticals.",
                "If any red flags arise (e.g. chest pressure, sudden breathing difficulty, fainting), call 112 immediately."
            ],
            "limitation": "Clinical Disclaimer: This rule-based triage assessment organizes health information for medical discussion. It is not an official medical diagnosis, laboratory test, or pathology report."
        }

    # --- TIER 3: GENERAL SELF-CARE GUIDANCE ---
    # Low-risk, short duration, mild symptoms without red flags
    return {
        "tier": "General self-care guidance",
        "tier_level": 3,
        "badge_color": "emerald",
        "headline": "💚 GENERAL SELF-CARE & HOME MONITORING GUIDANCE",
        "call_to_action": "Monitor symptoms at home with restorative self-care practices.",
        "emergency_numbers": ["112 (India Emergency)"],
        "category": "Mild / Early-Stage Wellness Management",
        "reasons": [
            "Reported symptoms appear mild in intensity with short duration.",
            "No acute red-flag indicators detected in preliminary triage rules."
        ],
        "urgent_actions": [
            "Prioritize adequate rest (7 to 9 hours) to allow your immune system to recover.",
            "Stay well hydrated with clean water, warm broths, or oral rehydration fluids.",
            "Record your daily temperature, meals, and sleep in the Wellness Tracker.",
            "If symptoms worsen, do not improve within 3 days, or new pain develops, consult a doctor."
        ],
        "limitation": "Informational Notice: The absence of detected emergency indicators does not guarantee that a serious condition is not present. Always listen to your body and consult a physician if in doubt."
    }

