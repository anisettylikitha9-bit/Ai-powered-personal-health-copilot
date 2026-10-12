# 🏥 Health Copilot AI — Advanced AI Personal Health Copilot

An intelligent, privacy-first, full-stack personal healthcare companion and clinical triage web application designed to empower individuals with safe, explainable health tracking, interactive 3D biometric visualizations, and multilingual symptom education.

Built with **React 19 + Vite**, **Tailwind CSS**, **Three.js (WebGL 3D)**, **React Router**, **Recharts**, **Lucide React**, **FastAPI**, **SQLAlchemy 2.0 ORM**, **Pydantic v2**, and **SQLite**.

**100% Functional Offline & Local**: Operates securely with a local SQLite database and conservative validated rule-based algorithms. Requires **zero paid APIs, zero API keys, and zero external cloud dependencies**, with optional local LLM integration support (e.g., Ollama).

---

## 🌟 1. Technology Stack

### Frontend
- **Framework**: React.js 19 with Vite 8
- **Styling**: Tailwind CSS (Modern healthcare theme with teal `#00838f`, cyan, and clean slate palettes)
- **3D Biometrics**: Three.js WebGL anatomical heartbeat telemetry and 3D bio-hologram canvas
- **Routing**: React Router (HashRouter / Navigation routes)
- **Charts & Visualization**: Recharts (Weekly & monthly hydration, sleep, exercise, and active day trends)
- **Icons**: Lucide React

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

## 🧭 2. Core Application Modules

1. **Personal Health Dashboard (`/dashboard`)**
   - **Emergency India Warning Bar**: High-visibility alert with direct one-click dialers for **Call 112 (India)** and **Ambulance: 108**.
   - **Personalized Healthcare Hub**: Welcome status with quick access to *Log Vitals* and *Reports & PDFs*.
   - **Interactive 3D Anatomical Suite**:
     - **3D Heart Canvas**: Real-time WebGL particle heart pulsing with live BPM telemetry, rotatable camera, and multi-view modes (*3D Heart*, *DNA Helix*, *Dual Matrix*).
     - **3D Biometric Hologram**: Concentric rotating holographic rings and wireframe core with live sync indicators (`Pulse`, `BP Target`, `Glucose`).
   - **Key Metrics Row**: Habit Score (0–100), Vitals records count, active prescriptions, scheduled clinic appointments, and stored medical PDFs.

2. **Health Profile & Privacy (`/profile`)**
   - Manage baseline age, gender, height, weight, blood group, allergies, chronic conditions, and emergency contacts.
   - Real-time WHO BMI calculation and classification.
   - **Permanent Privacy Data Eraser**: One-click GDPR-style permanent deletion of all personal vitals, logs, chats, and documents.

3. **Vitals Tracker (`/vitals`)**
   - Track Heart Rate (BPM), Blood Pressure (Systolic/Diastolic), Blood Glucose (mg/dL), Body Temperature (°F), and SpO2.
   - Anomaly detection flags alerting out-of-range physiological measurements.

4. **AI Health Assistant (`/assistant`)**
   - Multilingual conversational assistant supporting **English**, **తెలుగు (Telugu)**, and **Roman Telugu** (e.g., *"Naaku jwaram ga undi"*, *"Explain dehydration in Telugu"*).
   - Voice speech-to-text dictation and real-time medical speech synthesis (text-to-speech).
   - Clickable relevant follow-up questions, non-prescriptive medication safety directive, and statutory medical disclaimer.

5. **Symptom Checker & Emergency Triage (`/triage` / `/symptoms`)**
   - **Tier 1 (Emergency Care Now)**: Severe breathing difficulty, stroke signs (F.A.S.T.), unconsciousness, chest pain, uncontrolled bleeding -> Prominently instructs to **call 112** without waiting for chatbot responses.
   - **Tier 2 (Prompt Medical Consultation)**: Persistent symptoms (>3 days), severe intensity, or multi-symptom clusters -> Physician examination within 24–48 hours.
   - **Tier 3 (General Self-Care Guidance)**: Mild, short-duration concerns with home hydration and rest monitoring.

6. **Medicine Reminders (`/medicines`)**
   - Schedule daily prescriptions, dosage, timing, and food instructions (*Before Food / After Food*).
   - Daily adherence tracking and checklist completion.

7. **Doctor Appointments (`/appointments`)**
   - Schedule specialist clinic visits, dates, doctor names, and consultation notes.

8. **Daily Wellness Tracker (`/wellness`)**
   - Log daily water intake (ml), sleep duration (hours), exercise minutes & type, mood, and meals.
   - Interactive modal forms for **Add**, **Edit**, and **Delete** records.
   - Real-time habit scoring and personal goal progress indicators.

9. **Health Reports & Medical PDF Vault (`/reports`)**
   - Upload and securely store clinical laboratory PDFs, diagnostic scans, and doctor prescriptions.
   - Safe disk storage with one-click download, view, and deletion.

---

## 🇮🇳 3. Multilingual Support (Telugu + English)

Health Copilot AI provides native tri-lingual support:
- **English**: Full clinical documentation and guidance.
- **తెలుగు (Telugu Script)**: Native Telugu health terms, instructions, and emergency alerts.
- **Roman Telugu (Transliterated Telugu)**: Transliterated colloquial queries such as:
  - *"Naaku jwaram ga undi."* (I have a fever.)
  - *"Thala noppi ga undi em cheyyali?"* (I have a headache, what should I do?)
  - *"Neeti koratha gurinchi vivarana."* (Explanation of dehydration.)

---

## 🚀 4. Quickstart Guide

### Prerequisites
- **Node.js** (v18+) and **npm**
- **Python** (v3.10+)

### Step 1: Start Backend (FastAPI)
```bash
# 1. Activate Python virtual environment
.\.venv\Scripts\activate          # Windows PowerShell / CMD
# source .venv/bin/activate       # macOS / Linux

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Start the FastAPI server
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```
> The API will be live at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.

### Step 2: Start Frontend (React + Vite)
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

The application includes comprehensive automated test suites:

```bash
# Run backend clinical test suite
.\.venv\Scripts\python.exe backend/test_healthsaathi.py

# Run full integration test suite
.\.venv\Scripts\python.exe test_suite.py
```

### Verified Test Results:
- **13/13 Integration Test Suites Passed** (Authentication, Vitals flags, 6-point symptom engine, PDF vault, Habitation scoring).
- **6/6 Clinical Triage & REST API Suites Passed** (Emergency 112 routing, Multilingual Telugu responses, User isolation, SQLite ORM CRUD).

---

## 🔒 6. Security, Privacy & Medical Safety Principles

1. **Non-Diagnostic Safety Guarantee**: Health Copilot AI never provides definitive diagnoses or unverified disease labels. It structures educational information for clinical discussion.
2. **Never Delays Emergency Care**: Tier 1 red flags immediately display India's **112** helpline with bold alerts, telling users **not** to wait for chatbot responses.
3. **Absence of Keywords != Proof of Safety**: Conservative logic explicitly clarifies that lack of detected red flags does not guarantee benign condition.
4. **Data Isolation**: SQLite tables enforce foreign-key cascading and parameterized SQLAlchemy queries.
5. **Zero Data Tracking**: All health logs, biometrics, and documents stay locally on the user's machine.

---

## 👥 Authors & Repository
- **Repository**: [https://github.com/anisettylikitha9-bit/ai-powered-personal-health-copilot.git](https://github.com/anisettylikitha9-bit/ai-powered-personal-health-copilot.git)
- **Application**: Health Copilot AI — Advanced AI Personal Health Copilot
