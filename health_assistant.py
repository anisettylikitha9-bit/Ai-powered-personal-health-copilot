"""
health_assistant.py - Upgraded Symptom-Aware Transparent AI Health Assistant
Integrates symptom_engine for natural language symptom evaluation, emergency red-flag triage,
non-prescriptive medication safety, and transparent clinical wellness education.
Strictly non-diagnostic and non-prescriptive. No external paid APIs or models required.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
import symptom_engine
from translations import t

# ==============================================================================
# GENERAL LIFESTYLE & WELLNESS EDUCATION DATABASE
# ==============================================================================

LIFESTYLE_RULES = [
    {
        "category": "Dehydration Management",
        "rule_id": "RULE_DEHYDRATION",
        "keywords": ["dehydration", "dehydrated", "explain dehydration", "neeti koratha", "dehydration in telugu", "dehydration gurinchi"],
        "title": "Dehydration: Symptoms, Science & Rehydration",
        "response_en": (
            "💧 **Clinical Overview of Dehydration:**\n\n"
            "• **What is Dehydration?**: Dehydration occurs when your body loses more fluids and electrolytes than you take in, disrupting vital metabolic and cellular processes.\n"
            "• **Key Warning Signs**:\n"
            "  - Extreme thirst and parched dry mouth / lips.\n"
            "  - Infrequent urination or dark amber/brown-colored urine.\n"
            "  - Dizziness, lightheadedness, or feeling faint upon standing.\n"
            "  - Persistent fatigue, headache, and muscle cramps.\n"
            "• **Safe Home Recovery Steps**:\n"
            "  - Drink Oral Rehydration Solution (ORS), coconut water, or clean water with a pinch of salt and lemon.\n"
            "  - Avoid sugary sodas, concentrated fruit syrup, alcohol, and excessive tea/coffee.\n"
            "  - Sip fluids steadily rather than gulping massive amounts at once.\n"
            "• **Emergency Red Flags (Seek Care Now)**:\n"
            "  - Inability to keep any liquids down for > 12 hours, confusion, rapid weak pulse, or fainting."
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
            "• **అత్యవసర హెచ్చరిక**: నిరంతర వాంతులు, స్పృహ తప్పడం లేదా 12 గంటల పాటు ద్రవాలు తీసుకోలేకపోతే వెంటనే ఆసుపత్రికి వెళ్లండి."
        ),
        "response_roman": (
            "💧 **Dehydration (Neeti Koratha) Vivarana:**\n\n"
            "• **Dehydration Ante Enti?**: Mana shareeram theesukune dravamula kante ekkuva neellu kolpoyinappudu dehydration avuthundi.\n"
            "• **Mukhyamaina Lakshanalu**:\n"
            "  - Theevramaina daaham mariyu noru endipovadam.\n"
            "  - Moodhra rangam muduru pasupu rangulo undatam leda thakkuvaga ravadam.\n"
            "  - Kallu thiragadam, thala noppi, mariyu neerasam.\n"
            "• **Nivarana Mariyu Care Tips**:\n"
            "  - Ventane ORS fluid, fresh kobbari neellu, leda manchineellu thagandi.\n"
            "  - Majjiga theesukondi mariyu cool environment lo rest theesukondi.\n"
            "  - Cool drinks mariyu tea/coffee thagakandi.\n"
            "• **Emergency Note**: 12 hours nunchi vanthulu aagakapothe leda kallu thirigi padipothe ventane hospital ki vellali."
        ),
        "follow_ups": [
            "What are common dehydration symptoms?",
            "How much water should I drink daily?",
            "Tips for Oral Rehydration Solution (ORS)"
        ]
    },
    {
        "category": "Hydration Guidelines",
        "rule_id": "RULE_HYDRATION",
        "keywords": ["water", "hydrate", "hydration", "drink", "thirst", "fluid", "నీరు", "దాహం", "మంచినీరు"],
        "title": "Daily Water Intake & Hydration Science",
        "response_en": (
            "💧 **Optimal Daily Hydration Guidelines:**\n\n"
            "• **Standard Benchmark**: Healthy adults generally require **2.5 to 3.5 liters (10–14 glasses)** of fluids daily, depending on climate and activity.\n"
            "• **Rule of Thumb**: Approximately **30 to 35 ml per kilogram of body weight** daily.\n"
            "• **Indicators of Good Hydration**: Light, pale-straw colored urine throughout the day.\n"
            "• **Hydration Tips**:\n"
            "  - Drink 1–2 glasses upon waking to rehydrate.\n"
            "  - In warm Indian weather, supplement with natural coconut water, lemon water, or buttermilk.\n"
            "  - Sip water consistently rather than drinking large volumes infrequently."
        ),
        "response_te": (
            "💧 **రోజువారీ నీటి వినియోగ మార్గదర్శకాలు:**\n\n"
            "• **సాధారణ పరిమాణం**: ఆరోగ్యకరమైన పెద్దలు ప్రతిరోజూ **2.5 నుండి 3.5 లీటర్ల (10–14 గ్లాసులు)** నీరు లేదా ద్రవాలు తాగాలి.\n"
            "• **సూత్రం**: శరీర బరువులో ప్రతి కిలోకు సుమారు **30 నుండి 35 మి.లీ** నీరు అవసరం.\n"
            "• **మంచి సంకేతం**: మూత్రం లేత గడ్డి రంగులో ఉండటం సరైన హైడ్రేషన్‌కు సూచన.\n"
            "• **చిట్కాలు**: ఉదయం లేవగానే 1-2 గ్లాసుల నీరు తాగండి; కొబ్బరి నీరు, మజ్జిగ శరీరానికి మేలు చేస్తాయి."
        )
    },
    {
        "category": "Sleep Hygiene",
        "rule_id": "RULE_SLEEP",
        "keywords": ["sleep", "circadian", "bedtime", "restful", "sleep hygiene", "నిద్ర", "నిద్ర అలవాట్లు"],
        "title": "Sleep Hygiene & Circadian Optimization",
        "response_en": (
            "🌙 **Principles of Restorative Sleep:**\n\n"
            "• **Recommended Duration**: Adults require **7 to 9 hours** of quality sleep nightly.\n"
            "• **Sleep Debt**: Chronic sleep under 6 hours impairs glucose metabolism, cognitive function, and immunity.\n"
            "• **Practical Sleep Routine**:\n"
            "  - Maintain a consistent bedtime and wake-up time, even on weekends.\n"
            "  - Dim screens (blue light) at least 45–60 minutes before bed.\n"
            "  - Keep your sleeping environment cool, quiet, and dark.\n"
            "  - Avoid heavy caffeine (coffee, tea, energy drinks) after 2:00 PM."
        ),
        "response_te": (
            "🌙 **మంచి నిద్ర కోసం నియమాలు:**\n\n"
            "• **సమయం**: పెద్దలకు ప్రతి రాత్రి **7 నుండి 9 గంటల** నిద్ర అవసరం.\n"
            "• **నిద్ర నియమాలు**:\n"
            "  - ప్రతిరోజూ ఒకే సమయానికి పడుకోవడం మరియు మేల్కొనడం అలవాటు చేసుకోండి.\n"
            "  - పడుకునే 45-60 నిమిషాల ముందు మొబైల్/ల్యాప్‌టాప్ స్క్రీన్లను పక్కన పెట్టండి.\n"
            "  - పడకగదిని చల్లగా, నిశ్శబ్దంగా మరియు చీకటిగా ఉంచండి.\n"
            "  - మధ్యాహ్నం 2 గంటల తర్వాత కాఫీ, టీలకు దూరంగా ఉండండి."
        )
    },
    {
        "category": "Blood Pressure Education",
        "rule_id": "RULE_BP",
        "keywords": ["blood pressure", "bp", "hypertension", "systolic", "diastolic", "రక్తపోటు", "బీపీ"],
        "title": "Understanding Blood Pressure Readings",
        "response_en": (
            "💓 **Blood Pressure Standards (AHA / Indian Guidelines):**\n\n"
            "• **Normal Range**: Systolic **< 120 mmHg** AND Diastolic **< 80 mmHg**.\n"
            "• **Elevated**: Systolic **120–129 mmHg** AND Diastolic **< 80 mmHg**.\n"
            "• **Stage 1**: Systolic **130–139 mmHg** OR Diastolic **80–89 mmHg**.\n"
            "• **Stage 2**: Systolic **≥ 140 mmHg** OR Diastolic **≥ 90 mmHg**.\n"
            "• **Hypertensive Crisis**: Systolic **≥ 180 mmHg** or Diastolic **≥ 120 mmHg** (requires immediate medical care).\n"
            "• **Lifestyle Support (DASH Principles)**:\n"
            "  - Moderate dietary sodium (< 2,000 mg/day).\n"
            "  - Emphasize potassium-rich foods (bananas, spinach, coconut water).\n"
            "  - Engage in 30 minutes of aerobic exercise (brisk walking) daily.\n\n"
            "*(Never change or discontinue prescribed blood pressure medication without your physician's advice.)*"
        ),
        "response_te": (
            "💓 **రక్తపోటు (BP) ప్రమాణాలు:**\n\n"
            "• **సాధారణం**: సిస్టోలిక్ **< 120 mmHg** మరియు డయాస్టోలిక్ **< 80 mmHg**.\n"
            "• **ఎలివేటెడ్**: సిస్టోలిక్ **120–129 mmHg** మరియు డయాస్టోలిక్ **< 80 mmHg**.\n"
            "• **స్టేజ్ 1**: సిస్టోలిక్ **130–139 mmHg** లేదా డయాస్టోలిక్ **80–89 mmHg**.\n"
            "• **స్టేజ్ 2**: సిస్టోలిక్ **≥ 140 mmHg** లేదా డయాస్టోలిక్ **≥ 90 mmHg**.\n"
            "• **ఆహార మార్పులు**: ఉప్పు వాడకం తగ్గించండి, పండ్లు, కూరగాయలు మరియు రోజూ 30 నిమిషాల నడక అలవాటు చేసుకోండి."
        )
    },
    {
        "category": "Blood Glucose Literacy",
        "rule_id": "RULE_GLUCOSE",
        "keywords": ["glucose", "sugar", "diabetes", "fasting glucose", "postprandial", "hba1c", "చక్కెర", "మధుమేహం", "షుగర్"],
        "title": "Blood Glucose Reference Levels",
        "response_en": (
            "🩸 **Blood Glucose Reference Ranges:**\n\n"
            "• **Fasting Plasma Glucose (after 8+ hours fast)**:\n"
            "  - Normal: **70 – 99 mg/dL**\n"
            "  - Borderline / Impaired: **100 – 125 mg/dL**\n"
            "  - Elevated: **≥ 126 mg/dL** (requires physician confirmation)\n"
            "• **Postprandial Glucose (2 hours after meal)**:\n"
            "  - Normal: **< 140 mg/dL**\n"
            "• **Nutritional Balance**:\n"
            "  - Pair carbohydrates with dietary fiber and protein to prevent insulin spikes.\n"
            "  - Opt for whole grains (millets, oats, brown rice) instead of ultra-refined flours.\n"
            "  - Take a gentle 10-minute walk after substantial meals."
        ),
        "response_te": (
            "🩸 **రక్తంలో చక్కెర (గ్లూకోజ్) ప్రమాణాలు:**\n\n"
            "• **ఖాళీ కడుపుతో (ఫాస్టింగ్)**:\n"
            "  - సాధారణం: **70 – 99 mg/dL**\n"
            "  - ప్రీ-డయాబెటిస్: **100 – 125 mg/dL**\n"
            "  - డయాబెటిస్ స్థాయి: **≥ 126 mg/dL**\n"
            "• **భోజనం తర్వాత (2 గంటలకు)**: **< 140 mg/dL** సాధారణం.\n"
            "• తృణధాన్యాలు (చిరుధాన్యాలు, బ్రౌన్ రైస్) మరియు పీచు పదార్థాలు అధికంగా ఉండే ఆహారాన్ని ఎంచుకోండి."
        )
    },
    {
        "category": "Physical Activity & Fitness",
        "rule_id": "RULE_EXERCISE",
        "keywords": ["exercise", "workout", "steps", "gym", "cardio", "fitness", "aerobic", "physical activity", "వ్యాయామం", "నడక", "యోగా"],
        "title": "Exercise & Physical Activity Guidelines",
        "response_en": (
            "🏃 **Cardiometabolic Fitness Guidelines (WHO):**\n\n"
            "• **Weekly Target**: At least **150 minutes of moderate-intensity aerobic activity** (e.g., brisk walking, cycling) or 75 minutes of vigorous activity.\n"
            "• **Strength & Mobility**: Incorporate resistance or bodyweight exercises (squats, yoga) at least 2 days a week.\n"
            "• **Daily Step Target**: Aim for **7,000 to 10,000 steps** to maintain metabolic health and lower sedentary risks.\n"
            "• **Getting Started**: Start with a 15-minute daily walk and progressively increase duration."
        ),
        "response_te": (
            "🏃 **శారీరక శ్రమ & వ్యాయామ మార్గదర్శకాలు (WHO):**\n\n"
            "• **వారపు లక్ష్యం**: వారానికి కనీసం **150 నిమిషాల మోస్తరు వ్యాయామం** (చురుకైన నడక, సైక్లింగ్) లేదా 75 నిమిషాల తీవ్ర వ్యాయామం.\n"
            "• **రోజువారీ అడుగులు**: రోజుకు **7,000 నుండి 10,000 అడుగులు** నడవడం ఆరోగ్యానికి ఎంతో మంచిది.\n"
            "• వారానికి కనీసం 2 రోజులు యోగా లేదా కండరాల బలోపేత వ్యాయామాలు చేయండి."
        )
    },
    {
        "category": "Nutrition & Balanced Plate",
        "rule_id": "RULE_NUTRITION",
        "keywords": ["diet", "nutrition", "balanced plate", "protein", "fiber", "vegetables", "healthy food", "ఆహారం", "పోషకాహారం", "కూరగాయలు"],
        "title": "Principles of a Balanced Nutritional Plate",
        "response_en": (
            "🥗 **Healthy Plate Architecture:**\n\n"
            "• **50% of Plate**: Non-starchy vegetables and leafy greens (fiber, polyphenols, minerals).\n"
            "• **25% of Plate**: High-quality protein (lentils/dal, paneer, tofu, eggs, beans, fish).\n"
            "• **25% of Plate**: Complex unrefined carbohydrates (millets, brown rice, whole wheat roti, quinoa).\n"
            "• **Healthy Fats**: Moderate amounts of nuts (almonds, walnuts), seeds, and cold-pressed cooking oils.\n"
            "• **Limit**: Deep-fried snacks, ultra-processed foods, high-fructose beverages, and excess table salt."
        ),
        "response_te": (
            "🥗 **ఆరోగ్యకరమైన పోషకాహార ప్లేట్:**\n\n"
            "• **50% ప్లేట్**: ఆకుకూరలు మరియు కూరగాయలు (పీచు పదార్థాలు, విటమిన్లు).\n"
            "• **25% ప్లేట్**: ప్రొటీన్ ఆహారాలు (పప్పులు, పనీర్, గుడ్లు, చేపలు, మొలకలు).\n"
            "• **25% ప్లేట్**: సంక్లిష్ట కార్బోహైడ్రేట్లు (చిరుధాన్యాలు, బ్రౌన్ రైస్, గోధుమ రొట్టెలు).\n"
            "• వేపుళ్ళు, శీతల పానీయాలు మరియు అధిక ఉప్పును తగ్గించండి."
        )
    },
    {
        "category": "Heart Rate Literacy",
        "rule_id": "RULE_HEART_RATE",
        "keywords": ["heart rate", "pulse", "bpm", "beats per minute", "tachycardia", "bradycardia", "గుండె వేగం", "నాడి"],
        "title": "Resting Heart Rate & Pulse Assessment",
        "response_en": (
            "❤️ **Resting Heart Rate (HR) Standards:**\n\n"
            "• **Normal Adult Range**: **60 to 100 beats per minute (BPM)** measured at complete physical rest.\n"
            "• **Athletes**: Highly conditioned endurance athletes frequently have resting rates of **40–60 BPM**.\n"
            "• **Factors Affecting Pulse**: Dehydration, caffeine, fever, emotional stress, lack of sleep, and recent exercise.\n"
            "• **When to Seek Consultation**: If your resting rate persistently exceeds 100 BPM or drops below 50 BPM with dizziness or fatigue."
        ),
        "response_te": (
            "❤️ **గుండె వేగం (HR) ప్రమాణాలు:**\n\n"
            "• **సాధారణం**: విశ్రాంతి సమయంలో పెద్దలకు నిమిషానికి **60 నుండి 100 స్పందనలు (BPM)**.\n"
            "• **కారణాలు**: డీహైడ్రేషన్, కాఫీ, జ్వరం, ఒత్తిడి లేదా నిద్రలేమి వల్ల గుండె వేగం తాత్కాలికంగా పెరుగుతుంది.\n"
            "• విశ్రాంతి సమయంలో పల్స్ 100 కన్నా ఎక్కువ ఉంటే లేదా 50 కన్నా తక్కువ ఉండి కళ్ళు తిరిగితే వైద్యుడిని సంప్రదించండి."
        )
    },
    {
        "category": "Stress & Mental Relaxation",
        "rule_id": "RULE_STRESS",
        "keywords": ["stress", "anxiety", "meditation", "calm", "relax", "breathing technique", "4-7-8", "ఒత్తిడి", "ఆందోళన", "ధ్యానం"],
        "title": "Evidence-Based Stress Reduction & Breathing",
        "response_en": (
            "🧘 **Stress Reduction & Nervous System Downregulation:**\n\n"
            "• **The 4-7-8 Breathing Technique**:\n"
            "  1. Inhale quietly through your nose for **4 seconds**.\n"
            "  2. Hold your breath gently for **7 seconds**.\n"
            "  3. Exhale completely through your mouth with a soft whoosh for **8 seconds**.\n"
            "  4. Repeat cycle 4 times to stimulate the vagus nerve and promote calm.\n"
            "• **Workplace Micro-Breaks**: Step away from digital displays every 60 minutes for a 2-minute posture stretch."
        ),
        "response_te": (
            "🧘 **ఒత్తిడి నివారణ & శ్వాస పద్ధతులు:**\n\n"
            "• **4-7-8 శ్వాస పద్ధతి**:\n"
            "  1. ముక్కు ద్వారా 4 సెకన్ల పాటు శ్వాస తీసుకోండి.\n"
            "  2. శ్వాసను 7 సెకన్ల పాటు నిలిపి ఉంచండి.\n"
            "  3. నోటి ద్వారా 8 సెకన్ల పాటు శ్వాసను నెమ్మదిగా వదలండి.\n"
            "  4. దీనిని 4 సార్లు పునరావృతం చేయండి; ఇది నాడీ వ్యవస్థను శాంతింపజేస్తుంది."
        )
    },
    {
        "category": "BMI & Body Composition",
        "rule_id": "RULE_BMI",
        "keywords": ["bmi", "body mass index", "healthy weight", "overweight", "obesity", "బరువు", "ఊబకాయం"],
        "title": "Body Mass Index (BMI) & Metabolic Weight",
        "response_en": (
            "⚖️ **Body Mass Index (BMI) Reference:**\n\n"
            "• **Calculation**: Weight (kg) ÷ [Height (m)]²\n"
            "• **Categories (WHO International)**:\n"
            "  - Underweight: **< 18.5**\n"
            "  - Normal Weight: **18.5 – 24.9**\n"
            "  - Overweight: **25.0 – 29.9**\n"
            "  - Obesity: **≥ 30.0**\n"
            "• **Important Note**: BMI is a screening ratio. Waist circumference and muscle-to-fat ratio provide essential additional context."
        ),
        "response_te": (
            "⚖️ **శరీర ద్రవ్యరాశి సూచిక (BMI) ప్రమాణాలు:**\n\n"
            "• **లెక్కింపు**: బరువు (కిలోలు) ÷ [ఎత్తు (మీటర్లు)]²\n"
            "• **వర్గాలు**:\n"
            "  - తక్కువ బరువు: **< 18.5**\n"
            "  - సాధారణ బరువు: **18.5 – 24.9**\n"
            "  - అధిక బరువు: **25.0 – 29.9**\n"
            "  - ఊబకాయం: **≥ 30.0**"
        )
    }
]

DISCLAIMER_FOOTER_EN = (
    "\n\n---\n"
    "⚕️ *Notice: Transparent educational health literacy. This assistant runs on verified rule-based educational guidelines and is NOT a medical diagnosis or pharmaceutical prescription engine.*"
)

DISCLAIMER_FOOTER_TE = (
    "\n\n---\n"
    "⚕️ *గమనిక: ఇది విద్యా ప్రయోజనాల కోసం మాత్రమే. ఈ అసిస్టెంట్ ముందే నిర్వచించిన ఆరోగ్య నియమాల ఆధారంగా సమాధానాలు ఇస్తుంది; ఇది వైద్య నిర్ధారణ లేదా మందుల ప్రిస్క్రిప్షన్ కాదు.*"
)


# ==============================================================================
# UNIFIED INTENT MATCHER & RESPONSE GENERATOR
# ==============================================================================

def get_assistant_response(query: str, user_id: Optional[int] = None, lang: str = "en", **kwargs) -> Dict[str, Any]:
    """
    Evaluates user inquiry across a strict 5-stage clinical safety priority pipeline:
    Stage 1: High-Priority Emergency Detection (Red-Flag Triage & 112 Routing)
    Stage 2: Medicine Prescription / Tablet Inquiries (Strict Non-Prescription Safety)
    Stage 3: Symptom-Aware Assessment (Natural Language Parsing & 6-Point Structured Guide)
    Stage 4: Lifestyle & General Wellness Education (Hydration, Sleep, BP, Diet, etc.)
    Stage 5: Polite Greetings, Clarification & Unclear Input Guidance
    """
    clean_query = query.strip() if query else ""
    clean_lower = clean_query.lower()

    # Detect user language intent
    effective_lang = lang or "en"
    if "in telugu" in clean_lower or "telugu lo" in clean_lower or "telugulo" in clean_lower:
        effective_lang = "te"
    elif "in roman telugu" in clean_lower or "roman telugu" in clean_lower:
        effective_lang = "te-roman"
    elif re.search(r'[\u0C00-\u0C7F]', clean_query):
        effective_lang = "te"

    if effective_lang == "te":
        footer = DISCLAIMER_FOOTER_TE
    elif effective_lang == "te-roman":
        footer = "\n\n---\n⚕️ *Gamanika: Idi kevalam vidya mariyu wellness vishayam kosam matrame. Ee assistant doctor kaadu mariyu rogala nirdharana (diagnosis) cheyyadu.*"
    else:
        footer = DISCLAIMER_FOOTER_EN

    # Stage 0: Empty or very short input check
    if not clean_query or len(clean_query) < 2:
        unclear_res = symptom_engine.handle_unclear_or_greeting(clean_query, lang=effective_lang)
        return {
            "category": "Clarification Guidance",
            "rule_id": "RULE_UNCLEAR_INPUT",
            "title": "Please Describe Your Symptoms",
            "content": unclear_res["content"] + footer,
            "matched_rule": "Rule: Input Validation Guard (Prompting for clear symptom details)",
            "is_emergency": False,
            "follow_ups": [
                "I have a headache.",
                "Naaku jwaram ga undi.",
                "Explain dehydration in Telugu.",
                "How can I improve my sleep?"
            ]
        }

    # ==========================================================================
    # STAGE 1: EMERGENCY DETECTION (HIGHEST PRIORITY)
    # ==========================================================================
    emergency_check = symptom_engine.detect_emergency(clean_query, lang="te" if effective_lang == "te" else "en")
    if emergency_check:
        emergency_card = (
            f"### {emergency_check['headline']}\n\n"
            f"**⚠️ Category:** {emergency_check['matched_category']}\n\n"
            f"{emergency_check['description']}\n\n"
            f"📞 **EMERGENCY HELPLINE:** `{emergency_check['emergency_number']}`\n\n"
            f"**Immediate Safety Actions:**\n"
            + "\n".join([f"• {action}" for action in emergency_check["urgent_actions"]])
            + f"\n\n---\n*{emergency_check['limitations']}*"
        )
        return {
            "category": "Emergency Red-Flag Detection",
            "rule_id": emergency_check["rule_id"],
            "title": emergency_check["headline"],
            "content": emergency_card,
            "matched_rule": "🚨 Critical Rule: Emergency Triage Filter (Red-Flag Symptoms Identified)",
            "is_emergency": True,
            "follow_ups": [
                "Call 112 Emergency Hotline",
                "Nearest Hospital Casualty steps",
                "What to inform emergency ambulance?"
            ]
        }

    # ==========================================================================
    # STAGE 2: MEDICINE / TABLET REQUESTS (NON-PRESCRIPTIVE GUARD)
    # ==========================================================================
    med_check = symptom_engine.handle_medicine_inquiry(clean_query, user_id=user_id, lang="te" if effective_lang == "te" else "en")
    if med_check:
        med_card = (
            f"### {med_check['title']}\n\n"
            f"{med_check['intro']}\n\n"
            f"**Important Safety Principles:**\n"
            + "\n".join([f"• {p}" for p in med_check["principles"]])
        )

        # Include user's active prescriptions on record if available
        if med_check["active_prescriptions"]:
            med_card += f"\n\n---\n**{med_check['active_header']}**\n"
            for rx in med_check["active_prescriptions"]:
                med_card += f"• **{rx['name']}** ({rx['dosage']}) — Scheduled: `{rx['timing']}` | *Instructions: {rx['instructions']}*\n"
            med_card += "\n*(These are your own recorded prescriptions. Do not alter doses without speaking to your doctor.)*"

        return {
            "category": "Medication Safety Guidance",
            "rule_id": "RULE_MEDICINE_NON_PRESCRIPTIVE",
            "title": med_check["title"],
            "content": med_card + footer,
            "matched_rule": "Rule: Clinical Medication Safety & Non-Prescription Directive",
            "is_emergency": False,
            "follow_ups": [
                "How to record my prescribed medicines?",
                "When should I consult a doctor for medicines?",
                "Safe non-prescription home relief"
            ]
        }

    # ==========================================================================
    # STAGE 3: SYMPTOM-AWARE PARSING & STRUCTURED ASSESSMENT
    # ==========================================================================
    parsed_symptoms = symptom_engine.extract_symptoms_and_context(clean_query)
    if parsed_symptoms["matched_symptoms"]:
        assessment = symptom_engine.generate_symptom_assessment(
            symptoms=parsed_symptoms["matched_symptoms"],
            duration=parsed_symptoms["duration"],
            severity=parsed_symptoms["severity"],
            age_cue=parsed_symptoms["age_cue"],
            user_id=user_id,
            lang="te" if effective_lang == "te" else "en"
        )
        symptom_names = ", ".join(assessment["symptoms"])
        
        # Build Roman Telugu customized text if requested
        card_content = assessment["content"]
        if effective_lang == "te-roman":
            roman_names = ", ".join([s.get("name_roman", s["name_en"]) for s in parsed_symptoms["matched_symptoms"]])
            card_content = (
                f"### 📋 Arogya Lakshanalu & Self-Care Guidance (Roman Telugu)\n\n"
                f"**1. Meeru Cheppina Lakshanalu (Reported Symptoms):**\n"
                f"• Lakshanalu: **{roman_names}**\n\n"
                f"**2. Sadharana Karanamulu (Possible Common Causes):**\n"
                + "\n".join([f"• **{s.get('name_roman', s['name_en'])}**: {s.get('general_causes_roman', s['general_causes_en'])}" for s in parsed_symptoms["matched_symptoms"]]) + "\n\n"
                f"**3. Surakshithamaina Self-Care Charyalu (Safe Home Care):**\n"
                + "\n".join([f"• {item}" for s in parsed_symptoms["matched_symptoms"] for item in s.get("self_care_roman", s["self_care_en"])]) + "\n\n"
                f"**4. Doctor Ni Eppudu Kalavali (When to Contact Doctor):**\n"
                + "\n".join([f"• **{s.get('name_roman', s['name_en'])}**: {s['doctor_threshold_en']}" for s in parsed_symptoms["matched_symptoms"]]) + "\n\n"
                f"**5. Emergency Alert:**\n"
                f"🚨 *Severe chest pain, oopiri aadanappudu, leda spruha thappithe ventane **112** leda **108** ku call cheyyandi.*"
            )

        f_ups = assessment.get("follow_ups", [])
        if not f_ups:
            if effective_lang == "te":
                f_ups = ["ఈ లక్షణాలు ఎప్పటినుండి ఉన్నాయి?", "వైద్యుడిని ఎప్పుడు సంప్రదించాలి?", "ఇంట్లో చేయవలసిన జాగ్రత్తలు"]
            elif effective_lang == "te-roman":
                f_ups = ["Ee lakshanalu eppati nundi unnayi?", "Doctor ni eppudu kalavali?", "Intlo theesukovalsina care tips"]
            else:
                f_ups = ["When should I see a doctor?", "What safe home care should I follow?", "Are there emergency red flags?"]

        return {
            "category": "Symptom-Aware Assessment",
            "rule_id": "RULE_SYMPTOM_ASSESSMENT",
            "title": f"Health Guidance: {symptom_names}",
            "content": card_content + footer,
            "matched_rule": f"Rule: Symptom-Aware Educational Assessment [{symptom_names}]",
            "is_emergency": False,
            "follow_ups": f_ups
        }

    # ==========================================================================
    # STAGE 4: GENERAL LIFESTYLE & WELLNESS EDUCATION
    # ==========================================================================
    best_lifestyle = None
    best_score = 0

    for rule in LIFESTYLE_RULES:
        score = sum(1 for kw in rule["keywords"] if kw in clean_lower)
        if score > best_score:
            best_score = score
            best_lifestyle = rule

    if best_lifestyle and best_score > 0:
        if effective_lang == "te":
            resp_text = best_lifestyle.get("response_te", best_lifestyle["response_en"])
        elif effective_lang == "te-roman":
            resp_text = best_lifestyle.get("response_roman", best_lifestyle["response_en"])
        else:
            resp_text = best_lifestyle["response_en"]

        f_ups = best_lifestyle.get("follow_ups", [
            "How can I track this in my daily wellness tracker?",
            "What is the recommended daily target?",
            "How does this impact overall health?"
        ])

        return {
            "category": best_lifestyle["category"],
            "rule_id": best_lifestyle["rule_id"],
            "title": best_lifestyle["title"],
            "content": resp_text + footer,
            "matched_rule": f"Rule: General Wellness Knowledge Domain [{best_lifestyle['category']}]",
            "is_emergency": False,
            "follow_ups": f_ups
        }

    # ==========================================================================
    # STAGE 5: GREETINGS & UNCLEAR QUERIES FALLBACK
    # ==========================================================================
    fallback_res = symptom_engine.handle_unclear_or_greeting(clean_query, lang="te" if effective_lang == "te" else "en")
    
    if effective_lang == "te":
        sample_chips = [
            "నాకు తలనొప్పిగా ఉంది",
            "నాకు జ్వరంగా ఉంది",
            "డీహైడ్రేషన్ గురించి వివరించండి",
            "మంచి నిద్ర కోసం చిట్కాలు"
        ]
    elif effective_lang == "te-roman":
        sample_chips = [
            "Naaku jwaram ga undi.",
            "I have a headache.",
            "Explain dehydration in Telugu.",
            "How can I improve my sleep?"
        ]
    else:
        sample_chips = [
            "I have a headache.",
            "Naaku jwaram ga undi.",
            "Explain dehydration in Telugu.",
            "How can I improve my sleep?"
        ]

    return {
        "category": "Conversational Guidance",
        "rule_id": "RULE_GENERAL_FALLBACK",
        "title": "Personal Health Assistant",
        "content": fallback_res["content"] + footer,
        "matched_rule": "Rule: Conversational Clarification & Example Prompts",
        "is_emergency": False,
        "follow_ups": sample_chips
    }
