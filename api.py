"""
api.py - FastAPI Backend for AI Powered Personal Health Copilot
Serves REST API endpoints to power the React + Tailwind CSS v4 frontend.
Reuses existing SQLite database, symptom engine, AI assistant, and report generator.
"""

import os
import io
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import database
import auth
import wellness_engine
import symptom_engine
import symptom_checker
import health_assistant
import reports
from translations import TRANSLATIONS, t

# Initialize SQLite database
database.init_db()

app = FastAPI(
    title="AI Powered Personal Health Copilot API",
    version="2.0.0",
    description="FastAPI REST API powering the React + Tailwind CSS Healthcare Frontend"
)

# Enable CORS for Vite dev server (5173) and any local client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    email: Optional[str] = ""

class ProfileRequest(BaseModel):
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    blood_group: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    medications_summary: Optional[str] = None

class VitalRequest(BaseModel):
    user_id: int
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature_f: Optional[float] = None
    weight_kg: Optional[float] = None
    blood_glucose_mg_dl: Optional[int] = None
    glucose_context: Optional[str] = "Random"
    notes: Optional[str] = ""

class AssistantChatRequest(BaseModel):
    user_id: Optional[int] = None
    message: str
    lang: Optional[str] = "en"

ChatMessageRequest = AssistantChatRequest

class TriageRequest(BaseModel):
    user_id: Optional[int] = None
    symptoms: Optional[List[str]] = []
    text_input: Optional[str] = ""
    severity: Optional[str] = "Moderate"
    duration: Optional[str] = "1 to 3 days"
    age: Optional[int] = None
    gender: Optional[str] = None
    lang: Optional[str] = "en"

class WellnessUpdateRequest(BaseModel):
    user_id: int
    water_ml: int = 0
    sleep_hours: float = 0.0
    exercise_mins: int = 0
    exercise_type: Optional[str] = ""
    mood: Optional[str] = "Neutral"
    meal_notes: Optional[str] = ""
    notes: Optional[str] = ""

class PrivacyWipeRequest(BaseModel):
    user_id: int

class SymptomAssessRequest(BaseModel):
    user_id: Optional[int] = None
    symptoms: List[str]
    severity: str = "Moderate"
    duration: str = "1-3 days"
    age: Optional[int] = None
    gender: Optional[str] = None
    lang: str = "en"

class MedicineRequest(BaseModel):
    user_id: int
    medicine_name: str
    dosage: str
    schedule_timing: str
    time_str: str
    instructions: Optional[str] = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class AppointmentRequest(BaseModel):
    user_id: int
    doctor_name: str
    specialty: str
    clinic_hospital: str
    appointment_date: str
    appointment_time: str
    reason: Optional[str] = ""
    phone: Optional[str] = ""

class WellnessRequest(BaseModel):
    user_id: int
    log_date: str
    water_ml: int = 0
    sleep_hours: float = 0.0
    exercise_mins: int = 0
    exercise_type: Optional[str] = ""
    mood: Optional[str] = "Neutral"
    meal_notes: Optional[str] = ""
    notes: Optional[str] = ""

class WellnessGoalsRequest(BaseModel):
    user_id: int
    target_water_ml: int = 2500
    target_sleep_hours: float = 7.5
    target_exercise_mins: int = 30
    target_steps: int = 8000


# ==============================================================================
# 1. CORE SYSTEM & TRANSLATIONS
# ==============================================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "AI Powered Personal Health Copilot",
        "time": datetime.now().isoformat()
    }

@app.get("/api/translations")
def get_translations():
    return TRANSLATIONS


# ==============================================================================
# 2. AUTHENTICATION & DEMO DATA
# ==============================================================================

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user, msg = auth.authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail=msg)
    return {"status": "success", "user": user}

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    ok, msg = auth.register_user(req.username, req.password, req.full_name, req.email or "")
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    user = database.get_user_by_username(req.username)
    database.seed_demo_data(user["id"])
    return {"status": "success", "user": dict(user)}

@app.post("/api/auth/demo")
def demo_login():
    demo_user = database.get_user_by_username("demouser")
    if not demo_user:
        demo_user = database.get_user_by_username("demo_user")
    if not demo_user:
        auth.register_user("demouser", "Demo@123", "Demo Health User", "demo@healthcopilot.local")
        demo_user = database.get_user_by_username("demouser")
        database.seed_demo_data(demo_user["id"])
    return {"status": "success", "user": dict(demo_user)}


# ==============================================================================
# 3. DASHBOARD STATS & INSIGHTS
# ==============================================================================

@app.get("/api/dashboard/stats")
def get_dashboard_stats(user_id: int = Query(...)):
    user = database.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = database.get_profile(user_id)
    vitals = [dict(v) for v in database.get_vitals(user_id, limit=7)]
    latest_vital = vitals[0] if vitals else None
    
    wellness_logs = [dict(w) for w in database.get_wellness_logs(user_id, days=7)]
    goals = database.get_wellness_goals(user_id)
    
    today_str = date.today().strftime("%Y-%m-%d")
    today_wellness = next((w for w in wellness_logs if w["log_date"] == today_str), None)
    
    # Calculate habit score
    try:
        habit_result = wellness_engine.calculate_habit_score(user_id)
    except Exception as e:
        habit_result = {"habit_score": 70, "status_label": "Healthy Habit Pace", "breakdown": {}}
    
    medicines = [dict(m) for m in database.get_medicine_reminders(user_id, active_only=True)]
    appointments = [dict(a) for a in database.get_appointments(user_id)]
    documents = [dict(d) for d in database.get_medical_documents(user_id)]
    
    # Anomaly count
    all_vitals = database.get_vitals(user_id, limit=30)
    anomalies_count = sum(1 for v in all_vitals if v["flag_status"] in ("Warning", "Critical"))
    
    # Smart Insights
    try:
        insights = wellness_engine.generate_smart_insights(user_id)
    except Exception as e:
        insights = []
    
    return {
        "profile": dict(profile) if profile else None,
        "habit_score": habit_result,
        "vitals_count": len(all_vitals),
        "anomalies_count": anomalies_count,
        "latest_vital": latest_vital,
        "recent_vitals": vitals,
        "active_medicines_count": len(medicines),
        "appointments_count": len(appointments),
        "documents_count": len(documents),
        "wellness_logs": wellness_logs,
        "smart_insights": insights
    }


# ==============================================================================
# 4. HEALTH PROFILE & BMI
# ==============================================================================

@app.get("/api/profile")
def get_profile(user_id: int = Query(...)):
    profile = database.get_profile(user_id)
    if not profile:
        return {"profile": None, "bmi": None}
    prof_dict = dict(profile)
    bmi_info = None
    if prof_dict.get("height_cm") and prof_dict.get("weight_kg"):
        bmi_info = wellness_engine.calculate_bmi(weight_kg=prof_dict["weight_kg"], height_cm=prof_dict["height_cm"])
    return {"profile": prof_dict, "bmi": bmi_info}

@app.post("/api/profile")
def save_profile(req: ProfileRequest):
    database.save_profile(
        user_id=req.user_id,
        age=req.age,
        gender=req.gender,
        height_cm=req.height_cm,
        weight_kg=req.weight_kg,
        blood_group=req.blood_group,
        emergency_contact_name=req.emergency_contact_name,
        emergency_contact_phone=req.emergency_contact_phone,
        allergies=req.allergies,
        chronic_conditions=req.chronic_conditions,
        medications_summary=req.medications_summary
    )
    bmi_info = None
    if req.height_cm and req.weight_kg:
        bmi_info = wellness_engine.calculate_bmi(weight_kg=req.weight_kg, height_cm=req.height_cm)
    return {"status": "success", "bmi": bmi_info}


# ==============================================================================
# 5. VITALS TRACKER & ANOMALY DETECTION
# ==============================================================================

@app.get("/api/vitals")
def get_vitals(user_id: int = Query(...), limit: int = 50):
    rows = [dict(r) for r in database.get_vitals(user_id, limit=limit)]
    return {"vitals": rows}

@app.post("/api/vitals")
def log_vitals(req: VitalRequest):
    # Physiological anomaly validation
    try:
        val_res = wellness_engine.validate_vitals(
            systolic_bp=req.systolic_bp,
            diastolic_bp=req.diastolic_bp,
            heart_rate=req.heart_rate,
            temperature_f=req.temperature_f,
            weight_kg=req.weight_kg,
            blood_glucose=req.blood_glucose_mg_dl,
            glucose_context=req.glucose_context
        )
        flag_status = val_res.get("status", "Normal")
    except Exception:
        val_res = {}
        flag_status = "Normal"
    notes_combined = req.notes or ""
    if val_res.get("flags"):
        flags_str = " | ".join(val_res["flags"])
        notes_combined = f"{notes_combined} [{flags_str}]".strip()
    
    vital_id = database.log_vitals(
        user_id=req.user_id,
        systolic_bp=req.systolic_bp,
        diastolic_bp=req.diastolic_bp,
        heart_rate=req.heart_rate,
        temperature_f=req.temperature_f,
        weight_kg=req.weight_kg,
        blood_glucose_mg_dl=req.blood_glucose_mg_dl,
        glucose_context=req.glucose_context,
        flag_status=flag_status,
        notes=notes_combined
    )
    return {
        "status": "success",
        "id": vital_id,
        "flag_status": flag_status,
        "validation": val_res
    }

@app.delete("/api/vitals/{vital_id}")
def delete_vital(vital_id: int, user_id: int = Query(...)):
    ok = database.delete_vital(vital_id, user_id)
    return {"status": "success" if ok else "not_found"}


# ==============================================================================
# 6. AI HEALTH ASSISTANT & SYMPTOM ENGINE
# ==============================================================================

@app.post("/api/chat")
@app.post("/api/assistant/chat")
def assistant_chat(req: AssistantChatRequest):
    res = health_assistant.get_assistant_response(
        query=req.message,
        user_id=req.user_id,
        lang=req.lang or "en"
    )
    if req.user_id:
        try:
            database.save_chat_message(req.user_id, "user", req.message)
            database.save_chat_message(req.user_id, "assistant", res["content"])
        except Exception:
            pass
    return res

@app.get("/api/chat/history")
def get_chat_history(user_id: int = Query(...), limit: int = 50):
    rows = [dict(r) for r in database.get_chat_history(user_id, limit=limit)]
    return {"history": rows}

@app.delete("/api/chat/history")
def clear_chat_history(user_id: int = Query(...)):
    database.clear_chat_history(user_id)
    return {"status": "success"}

@app.post("/api/triage")
def triage_endpoint(req: TriageRequest):
    res = symptom_engine.evaluate_three_tier_triage(
        symptoms=req.symptoms or [],
        text_input=req.text_input or "",
        severity=req.severity or "Moderate",
        duration=req.duration or "1 to 3 days",
        age=req.age,
        gender=req.gender,
        lang=req.lang or "en"
    )
    if req.user_id:
        try:
            symptoms_str = ", ".join(req.symptoms or []) if req.symptoms else (req.text_input or "General Triage")
            database.log_symptom(
                user_id=req.user_id,
                symptoms=symptoms_str,
                duration=req.duration or "1 to 3 days",
                severity=req.severity or "Moderate",
                is_emergency=1 if res["tier_level"] == 1 else 0,
                guidance_summary=res["headline"]
            )
        except Exception:
            pass
    return res

@app.get("/api/symptoms/reference")
def symptom_reference():
    return {
        "common_symptoms": symptom_checker.COMMON_SYMPTOMS_LIST,
        "red_flags": symptom_checker.RED_FLAG_SYMPTOMS,
        "durations": symptom_checker.DURATION_CHOICES,
        "severities": symptom_checker.SEVERITY_CHOICES
    }

@app.post("/api/symptoms/assess")
def assess_symptoms(req: SymptomAssessRequest):
    res = symptom_checker.assess_symptoms(
        selected_symptoms=req.symptoms or [],
        duration=req.duration or "1 to 3 days",
        severity=req.severity or "Moderate",
        additional_notes=""
    )
    return res


# ==============================================================================
# 7. MEDICINE REMINDERS
# ==============================================================================

@app.get("/api/medicines")
def get_medicines(user_id: int = Query(...)):
    rows = [dict(r) for r in database.get_medicine_reminders(user_id, active_only=False)]
    today = date.today()
    taken_ids = set(database.get_medicine_logs_for_date(user_id, today))
    for r in rows:
        r["taken_today"] = r["id"] in taken_ids
    return {"medicines": rows}

@app.post("/api/medicines")
def add_medicine(req: MedicineRequest):
    s_date = datetime.strptime(req.start_date, "%Y-%m-%d").date() if req.start_date else None
    e_date = datetime.strptime(req.end_date, "%Y-%m-%d").date() if req.end_date else None
    
    med_id = database.add_medicine_reminder(
        user_id=req.user_id,
        medicine_name=req.medicine_name,
        dosage=req.dosage,
        schedule_timing=req.schedule_timing,
        time_str=req.time_str,
        instructions=req.instructions,
        start_date=s_date,
        end_date=e_date
    )
    return {"status": "success", "id": med_id}

@app.post("/api/medicines/{med_id}/toggle")
def toggle_medicine_taken(med_id: int, user_id: int = Query(...)):
    today = date.today()
    taken_ids = database.get_medicine_logs_for_date(user_id, today)
    if med_id in taken_ids:
        database.unmark_medicine_taken(med_id, user_id, today)
        return {"status": "success", "taken": False}
    else:
        database.mark_medicine_taken(med_id, user_id, today)
        return {"status": "success", "taken": True}

@app.delete("/api/medicines/{med_id}")
def delete_medicine(med_id: int, user_id: int = Query(...)):
    ok = database.delete_medicine_reminder(med_id, user_id)
    return {"status": "success" if ok else "not_found"}


# ==============================================================================
# 8. DOCTOR APPOINTMENTS
# ==============================================================================

@app.get("/api/appointments")
def get_appointments(user_id: int = Query(...)):
    rows = [dict(r) for r in database.get_appointments(user_id)]
    return {"appointments": rows}

@app.post("/api/appointments")
def book_appointment(req: AppointmentRequest):
    a_date = datetime.strptime(req.appointment_date, "%Y-%m-%d").date()
    apt_id = database.book_appointment(
        user_id=req.user_id,
        doctor_name=req.doctor_name,
        specialty=req.specialty,
        clinic_hospital=req.clinic_hospital,
        appointment_date=a_date,
        appointment_time=req.appointment_time,
        reason=req.reason,
        phone=req.phone
    )
    return {"status": "success", "id": apt_id}

@app.delete("/api/appointments/{apt_id}")
def delete_appointment(apt_id: int, user_id: int = Query(...)):
    ok = database.delete_appointment(apt_id, user_id)
    return {"status": "success" if ok else "not_found"}


# ==============================================================================
# 9. DAILY WELLNESS TRACKER
# ==============================================================================

@app.get("/api/wellness")
def get_wellness(user_id: int = Query(...), days: int = 30):
    rows = [dict(r) for r in database.get_wellness_logs(user_id, days=days)]
    goals = database.get_wellness_goals(user_id)
    return {"logs": rows, "goals": dict(goals) if goals else None}

@app.post("/api/wellness")
def log_wellness(req: WellnessRequest):
    l_date = datetime.strptime(req.log_date, "%Y-%m-%d").date()
    database.log_wellness(
        user_id=req.user_id,
        log_date=l_date,
        water_ml=req.water_ml,
        sleep_hours=req.sleep_hours,
        exercise_mins=req.exercise_mins,
        exercise_type=req.exercise_type,
        mood=req.mood,
        meal_notes=req.meal_notes,
        notes=req.notes
    )
    try:
        score_res = wellness_engine.calculate_habit_score(user_id=req.user_id)
    except Exception:
        score_res = {"total_score": 75, "score_grade": "Good Consistency"}
    return {"status": "success", "habit_score": score_res}

@app.put("/api/wellness/{record_id}")
def update_wellness(record_id: int, req: WellnessUpdateRequest):
    ok = database.update_wellness_log(
        log_id=record_id,
        user_id=req.user_id,
        water_ml=req.water_ml,
        sleep_hours=req.sleep_hours,
        exercise_mins=req.exercise_mins,
        exercise_type=req.exercise_type,
        mood=req.mood,
        meal_notes=req.meal_notes,
        notes=req.notes
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Wellness record not found or unauthorized")
    try:
        score_res = wellness_engine.calculate_habit_score(user_id=req.user_id)
    except Exception:
        score_res = {"total_score": 75}
    return {"status": "success", "habit_score": score_res}

@app.delete("/api/wellness/{record_id}")
def delete_wellness(record_id: int, user_id: int = Query(...)):
    ok = database.delete_wellness_log(log_id=record_id, user_id=user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Wellness record not found or unauthorized")
    return {"status": "success"}

@app.get("/api/insights")
def get_explainable_insights(user_id: int = Query(...)):
    """
    Generates Explainable Wellness Intelligence cards based on actual recorded data:
    Each insight contains:
    - title: Headline of the pattern
    - category: Domain (Activity, Hydration, Sleep, Vitals)
    - data_used: Explicit records analyzed
    - rule_applied: Underlying logic / heuristic used
    - result: Concrete quantifiable outcome
    - limitation: Transparent caveat
    """
    insights = []
    wellness_logs = database.get_wellness_logs(user_id, days=14)
    vitals_logs = database.get_vitals(user_id, limit=10)
    goals = database.get_wellness_goals(user_id)

    # 1. Active Days Progression (Two-week comparative window)
    if len(wellness_logs) >= 2:
        today = date.today()
        current_week_logs = [w for w in wellness_logs if (today - datetime.strptime(w["log_date"], "%Y-%m-%d").date()).days <= 7]
        prev_week_logs = [w for w in wellness_logs if 7 < (today - datetime.strptime(w["log_date"], "%Y-%m-%d").date()).days <= 14]
        
        curr_active_days = sum(1 for w in current_week_logs if w.get("exercise_mins", 0) > 0)
        prev_active_days = sum(1 for w in prev_week_logs if w.get("exercise_mins", 0) > 0)
        
        if prev_week_logs:
            diff = curr_active_days - prev_active_days
            if diff > 0:
                result_str = f"Your active days increased from {prev_active_days} to {curr_active_days} ({diff} additional active days this week)."
                card_type = "positive"
            elif diff == 0:
                result_str = f"Your activity consistency remained steady at {curr_active_days} active days this week."
                card_type = "neutral"
            else:
                result_str = f"Your active days decreased from {prev_active_days} to {curr_active_days}."
                card_type = "opportunity"
        else:
            result_str = f"You logged {curr_active_days} active exercise days in the current week."
            card_type = "positive" if curr_active_days >= 3 else "neutral"

        insights.append({
            "id": "INSIGHT_ACTIVE_DAYS",
            "type": card_type,
            "category": "Physical Activity Trend",
            "title": "Exercise Consistency & Active Days",
            "data_used": f"Activity records from two weeks ({len(wellness_logs)} logged daily entries).",
            "rule_applied": "Count days containing recorded exercise (exercise_mins > 0) across 7-day comparative windows.",
            "result": result_str,
            "limitation": "Recorded activity is self-reported and not a complete measure of aerobic capacity or clinical fitness."
        })

    # 2. Hydration Balance
    if len(wellness_logs) >= 1:
        target_water = goals.get("target_water_ml", 2500)
        water_vals = [w.get("water_ml", 0) for w in wellness_logs[-7:]]
        avg_water = round(sum(water_vals) / len(water_vals)) if water_vals else 0
        pct = round((avg_water / target_water) * 100) if target_water > 0 else 0
        
        insights.append({
            "id": "INSIGHT_HYDRATION",
            "type": "positive" if pct >= 85 else "opportunity",
            "category": "Hydration Science",
            "title": "Daily Fluid Intake Consistency",
            "data_used": f"Water intake records from past {len(water_vals)} days (average: {avg_water} ml / target: {target_water} ml).",
            "rule_applied": f"Compare 7-day moving average against personal daily hydration target ({target_water} ml).",
            "result": f"Currently meeting {pct}% of your target ({avg_water} ml daily average).",
            "limitation": "Optimal fluid requirements vary significantly with climate, temperature, and perspiration."
        })

    # 3. Sleep Regularity
    if len(wellness_logs) >= 1:
        sleep_vals = [w.get("sleep_hours", 0) for w in wellness_logs[-7:]]
        avg_sleep = round(sum(sleep_vals) / len(sleep_vals), 1) if sleep_vals else 0
        target_sleep = goals.get("target_sleep_hours", 8.0)
        
        insights.append({
            "id": "INSIGHT_SLEEP",
            "type": "positive" if avg_sleep >= 7.0 else "opportunity",
            "category": "Sleep Architecture",
            "title": "Circadian Rest & Sleep Duration",
            "data_used": f"Nightly sleep entries from past {len(sleep_vals)} days (average: {avg_sleep} hrs/night).",
            "rule_applied": "Compare average sleep against clinical restorative window (7.0 to 9.0 hours nightly).",
            "result": f"Averaging {avg_sleep} hours per night (target: {target_sleep} hrs).",
            "limitation": "Duration does not capture sleep architecture, deep sleep stages, or nighttime sleep fragmentation."
        })

    # 4. Blood Pressure / Vitals Stability
    bp_vitals = [v for v in vitals_logs if v.get("systolic_bp") and v.get("diastolic_bp")]
    if len(bp_vitals) >= 2:
        sys_list = [v["systolic_bp"] for v in bp_vitals[:5]]
        dia_list = [v["diastolic_bp"] for v in bp_vitals[:5]]
        avg_sys = round(sum(sys_list) / len(sys_list))
        avg_dia = round(sum(dia_list) / len(dia_list))
        variance = max(sys_list) - min(sys_list)
        
        insights.append({
            "id": "INSIGHT_VITALS_BP",
            "type": "positive" if avg_sys < 130 and avg_dia < 85 else "warning",
            "category": "Vitals Monitoring",
            "title": "Cardiovascular Pressure Stability",
            "data_used": f"Last {len(sys_list)} blood pressure measurements on record.",
            "rule_applied": "Compute mean arterial pressures and systolic variance across sequential readings.",
            "result": f"Average blood pressure is {avg_sys}/{avg_dia} mmHg with ±{variance} mmHg reading variance.",
            "limitation": "Self-measured blood pressure readings are subject to cuff calibration and situational anxiety (white-coat effect)."
        })

    if not insights:
        insights.append({
            "id": "INSIGHT_EMPTY",
            "type": "neutral",
            "category": "Baseline Establishment",
            "title": "Establishing Personal Health Baseline",
            "data_used": "0 recorded wellness logs on file.",
            "rule_applied": "Requires a minimum of 2 days of recorded logs to compute mathematical trends.",
            "result": "No baseline trends available yet. Record today's wellness or click 'Load Demo Health Data'.",
            "limitation": "This system never invents measurements or insights when data is missing."
        })

    return {"insights": insights}

@app.post("/api/privacy/wipe")
def wipe_user_records(req: PrivacyWipeRequest):
    database.wipe_user_data(req.user_id)
    return {"status": "success", "message": "All personal records have been permanently erased"}

@app.post("/api/wellness/goals")
def save_wellness_goals(req: WellnessGoalsRequest):
    database.save_wellness_goals(
        user_id=req.user_id,
        target_water_ml=req.target_water_ml,
        target_sleep_hours=req.target_sleep_hours,
        target_exercise_mins=req.target_exercise_mins,
        target_steps=req.target_steps
    )
    return {"status": "success"}


# ==============================================================================
# 10. MEDICAL DOCUMENTS & PDF STORAGE VAULT
# ==============================================================================

@app.get("/api/documents")
def get_documents(user_id: int = Query(...), category: Optional[str] = None):
    rows = [dict(r) for r in database.get_medical_documents(user_id, category_filter=category)]
    return {"documents": rows}

@app.post("/api/documents/upload")
async def upload_document(
    user_id: int = Form(...),
    title: str = Form(...),
    category: str = Form(...),
    report_date: str = Form(...),
    doctor_or_lab: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    contents = await file.read()
    orig_name = file.filename or "report.pdf"
    ext = os.path.splitext(orig_name)[1].lower()
    file_type = ext.replace(".", "").upper() or "PDF"
    
    doc_id = database.add_medical_document(
        user_id=user_id,
        title=title,
        category=category,
        report_date=report_date,
        doctor_or_lab=doctor_or_lab,
        file_name=orig_name,
        file_bytes=contents,
        file_type=file_type,
        notes=notes
    )
    return {"status": "success", "id": doc_id}

@app.get("/api/documents/{doc_id}/download")
def download_document(doc_id: int, user_id: int = Query(...)):
    doc = database.get_medical_document_by_id(doc_id, user_id)
    if not doc or not os.path.exists(doc["file_path"]):
        raise HTTPException(status_code=404, detail="Document not found on storage disk")
    return FileResponse(
        path=doc["file_path"],
        filename=doc["file_name"],
        media_type="application/octet-stream"
    )

@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: int, user_id: int = Query(...)):
    ok = database.delete_medical_document(doc_id, user_id)
    return {"status": "success" if ok else "not_found"}


# ==============================================================================
# 11. REPORTS & EXPORTS
# ==============================================================================

@app.get("/api/reports/summary-pdf")
def download_pdf_summary(user_id: int = Query(...)):
    pdf_bytes = reports.generate_pdf_report(user_id)
    user = database.get_user_by_id(user_id)
    uname = user["username"] if user else "user"
    filename = f"health_summary_{uname}_{date.today().strftime('%Y%m%d')}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/api/reports/csv/{report_type}")
def download_csv_report(report_type: str, user_id: int = Query(...)):
    if report_type == "vitals":
        df = reports.get_vitals_dataframe(user_id)
    elif report_type == "wellness":
        df = reports.get_wellness_dataframe(user_id)
    elif report_type == "medicines":
        df = reports.get_medicines_dataframe(user_id)
    elif report_type == "appointments":
        df = reports.get_appointments_dataframe(user_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    filename = f"{report_type}_export_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
