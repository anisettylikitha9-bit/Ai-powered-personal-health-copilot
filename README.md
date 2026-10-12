# 🏥 HealthSaathi AI — Advanced AI Personal Health Copilot

An intelligent, privacy-first, full-stack personal healthcare companion and clinical triage web application designed to empower individuals with safe, explainable health tracking and multilingual symptom education.

Built with **React 19 + Vite**, **Tailwind CSS**, **React Router**, **Recharts**, **Lucide React**, **FastAPI**, **SQLAlchemy 2.0 ORM**, **Pydantic v2**, and **SQLite**.

**100% Functional Offline & Local**: Operates securely with a local SQLite database and conservative validated rule-based algorithms. Requires **zero paid APIs, zero API keys, and zero external cloud dependencies**, with optional local LLM integration support (e.g., Ollama).

---

## 🌟 1. Technology Stack

### Frontend
- **Framework**: React.js 19 with Vite 8
- **Styling**: Tailwind CSS
- **Routing**: React Router (HashRouter / Navigation routes)
- **Charts & Visualization**: Recharts (Weekly & monthly hydration, sleep, exercise, and active day trends)
- **Icons**: Lucide React
- **3D Biometrics**: Three.js WebGL anatomical heartbeat telemetry and bio-hologram canvas

### Backend
- **Framework**: FastAPI (Asynchronous REST API)
- **Database**: SQLite with parameterized operations via SQLAlchemy 2.0 ORM
- **Validation**: Pydantic v2 schemas
- **Authentication**: Salted PBKDF2-HMAC-SHA256 password hashing (constant-time verification)
- **Server**: Uvicorn ASGI

### AI & Clinical Engine
- **Symptom Engine**: 6-part structured non-diagnostic educational guidance
- **Emergency Triage**: 3-tier clinical protocol routing acute red flags immediately to India's Emergency Number **112** (and Ambulance **108**)
- **Optional Local LLM**: Pluggable support for local Ollama/daemon endpoints (`http://localhost:11434/api/generate`) with graceful zero-delay fallback to rule-based engine
- **Zero Paid APIs**: App remains completely functional without any third-party service

---

## 🧭 2. Core Application Pages (9 Modules)

1. **Landing Page (`/` / `/landing`)**
   - High-visibility medical emergency banner with direct **112** dialing.
   - Interactive feature overview, clinical safeguards, offline privacy badges, and one-click demo launch.

2. **Login & Registration (`/login`)**
   - Secure account registration and authentication.
   - Interactive 3D WebGL biometrics demonstration and Instant Demo Access (`demouser`).

3. **Personal Health Dashboard (`/dashboard`)**
   - Personalized greeting, Health Habit Score (0–100) with status labels.
   - Real-time 3D anatomical cardiovascular canvas and bio-holographic vital visualizer.
   - Quick log access for vitals, wellness, prescriptions, and reports.

4. **AI Health Assistant (`/assistant`)**
   - Multilingual conversational assistant supporting **English**, **తెలుగు (Telugu)**, and **Roman Telugu** (e.g., *"Naaku jwaram ga undi"*, *"Explain dehydration in Telugu"*).
   - Voice speech-to-text dictation and real-time medical speech synthesis (text-to-speech).
   - Clickable relevant follow-up questions, non-prescriptive medication safety directive, and statutory medical disclaimer.

5. **Emergency Triage System (`/triage`)**
   - **Tier 1 (Emergency Care Now)**: Severe breathing difficulty, stroke signs (F.A.S.T.), unconsciousness, chest pain, uncontrolled bleeding -> Prominently instructs to **call 112** without waiting for chatbot responses.
   - **Tier 2 (Prompt Medical Consultation)**: Persistent symptoms (>3 days), severe intensity, or multi-symptom clusters -> Physician examination within 24–48 hours.
   - **Tier 3 (General Self-Care Guidance)**: Mild, short-duration concerns with home hydration and rest monitoring.

6. **Daily Wellness Tracker (`/wellness`)**
   - Log daily water intake (ml), sleep duration (hours), exercise minutes & type, mood, and meals.
   - Interactive modal forms for **Add**, **Edit**, and **Delete** records.
   - Real-time habit scoring and personal goal progress indicators.

7. **Explainable Wellness Intelligence & Analytics (`/analytics`)**
   - Mathematical progression cards computed strictly from real saved entries.
   - Every card explicitly details:
     - **📊 Data used**: Explicit records analyzed (e.g., *"Activity records from two weeks (6 logged daily entries)"*).
     - **⚙️ Rule applied**: Mathematical logic applied (e.g., *"Count days containing recorded exercise across 7-day comparative windows"*).
     - **🎯 Result**: Quantifiable outcome (e.g., *"Your active days increased from 2 to 4"*).
     - **⚠️ Limitation**: Transparent clinical caveat (*"Recorded activity is self-reported and not a complete measure of aerobic fitness"*).
   - Recharts visual charts for Hydration, Sleep duration, Exercise minutes, and Active Days.
   - Explicit empty state when no records exist (never invents measurements).

8. **Chat History Archives (`/history`)**
   - Chronological transcript of health questions, symptom evaluations, and recommendations.
   - Real-time keyword filter search and permanent one-click conversation wipe.

9. **Profile & Privacy Settings (`/profile`)**
   - Manage baseline age, gender, height, weight, blood group, allergies, chronic conditions, and emergency contacts.
   - Real-time WHO BMI calculation and classification.
   - **Permanent Privacy Data Eraser**: One-click GDPR-style permanent deletion of all personal vitals, logs, chats, and documents.

---

## 🇮🇳 3. Multilingual Support (Telugu + English)

HealthSaathi AI provides complete native tri-lingual support:
- **English**: Full clinical documentation and guidance.
- **తెలుగు (Telugu Script)**: Native Telugu health terms, instructions, and emergency alerts.
- **Roman Telugu (Transliterated Telugu)**: Transliterated colloquial queries such as:
  - *"Naaku jwaram ga undi."* (I have a fever.)
  - *"Thala noppi ga undi em cheyyali?"* (I have a headache, what should I do?)
  - *"Neeti koratha gurinchi vivarana."* (Explanation of dehydration.)

---

## 🚀 4. Run Instructions

### Prerequisites
- **Node.js** (v18+) and **npm**
- **Python** (v3.10+)

### Step 1: Start Backend (FastAPI)
Open a terminal in the project directory:

```bash
# 1. Activate Python virtual environment
.\.venv\Scripts\activate          # Windows PowerShell / CMD
# source .venv/bin/activate       # macOS / Linux

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Start the FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
> The API will be live at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.

### Step 2: Start Frontend (React + Vite)
Open a second terminal:

```bash
# 1. Navigate to frontend folder
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite development server
npm run dev
```
> The web application will launch at `http://localhost:5173`. Vite automatically proxies `/api` calls to `http://127.0.0.1:8000`.

---

## 🧪 5. Testing & Verification

The repository includes an automated verification test suite verifying all 6 clinical and functional modules:

```bash
.\.venv\Scripts\python.exe backend/test_healthsaathi.py
```

### Verified Test Results:
```text
--- 1. Testing Emergency Triage Detection ---
  [PASS] Emergency detected for 'severe chest pain and pressure...' -> Cardiac / Acute Chest Pain
  [PASS] Emergency detected for 'difficulty breathing cannot br...' -> Severe Respiratory Distress
  [PASS] Emergency detected for 'facial drooping and slurred sp...' -> Possible Stroke Warning Signs (F.A.S.T.)
  [PASS] Emergency detected for 'unconscious passed out on the ...' -> Unconsciousness / Severe Syncope
  [PASS] Emergency detected for 'severe bleeding coughing up bl...' -> Severe Uncontrolled Bleeding
  [PASS] Tier 1 'Emergency care now' confirmed.
  [PASS] Tier 2 'Prompt medical consultation' confirmed.
  [PASS] Tier 3 'General self-care guidance' confirmed.

--- 2. Testing Multilingual Conversational Health Assistant ---
  [PASS] 'I have a headache.' -> Correctly answered with follow-ups and disclaimer.
  [PASS] 'Naaku jwaram ga undi.' -> Correctly identified in Roman Telugu.
  [PASS] 'Explain dehydration in Telugu.' -> Provided Telugu clinical explanation.
  [PASS] 'How can I improve my sleep?' -> Provided circadian sleep guidance.

--- 3. Testing Authentication & User Isolation ---
  [PASS] User registered with ID: 21
  [PASS] Duplicate username correctly rejected.
  [PASS] Valid login succeeded.
  [PASS] Invalid password correctly rejected.

--- 4. Testing Wellness Tracker CRUD Operations ---
  [PASS] Created wellness log #204 for date 2026-10-10
  [PASS] Retrieved 1 wellness logs for user.
  [PASS] Updated wellness log successfully.
  [PASS] Habit score calculated: 100/100 (Exceptional Habits)
  [PASS] Deleted wellness log #204.

--- 5. Testing Explainable Wellness Intelligence with Real Data ---
  [PASS] Explainable card verified: 'Your active days increased from 2 to 4 (2 additional active days).'
         Data used: Activity records from two weeks (6 logged daily entries).
         Rule applied: Count days containing recorded exercise (exercise_mins > 0) across 7-day comparative windows.
         Limitation: Recorded activity is self-reported and not a complete measure of aerobic capacity or clinical fitness.

--- 6. Testing FastAPI REST API Endpoints ---
  [PASS] GET /api/health -> 200 OK
  [PASS] GET /api/translations -> 200 OK (en, te, te-roman)
  [PASS] POST /api/chat -> 200 OK
  [PASS] POST /api/triage -> 200 OK (Tier 1)
  [PASS] POST /api/wellness -> 200 OK (created #211)
  [PASS] GET /api/wellness -> 200 OK (7 logs returned)
  [PASS] PUT /api/wellness/211 -> 200 OK
  [PASS] DELETE /api/wellness/211 -> 200 OK
  [PASS] GET /api/insights -> 200 OK
  [PASS] GET /api/chat/history -> 200 OK

============================================================
SUCCESS: ALL 6 COMPREHENSIVE TEST SUITES PASSED FLAWLESSLY!
============================================================
```

---

## 🔒 6. Security, Privacy & Medical Safety Principles

1. **Non-Diagnostic Safety Guarantee**: HealthSaathi AI never provides definitive diagnoses or unverified disease labels. It structures educational information for clinical discussion.
2. **Never Delays Emergency Care**: Tier 1 red flags immediately display India's **112** helpline with bold alerts, telling users **not** to wait for chatbot responses.
3. **Absence of Keywords != Proof of Safety**: Conservative logic explicitly clarifies that lack of detected red flags does not guarantee benign condition.
4. **Data Isolation**: SQLite tables enforce foreign-key cascading and parameterized SQLAlchemy queries.
5. **No Data Broker Sharing**: All health logs, biometrics, and documents stay locally on the user's machine.

---

## 👥 Authors & License
Developed for HealthSaathi AI — Advanced AI Personal Health Copilot. Open educational and personal wellness tool.
