"""
backend/app/main.py - HealthSaathi AI FastAPI REST API Server
Exposes all endpoints required for React frontend with SQLAlchemy ORM and SQLite backend.
"""

import sys
import os

# Ensure backend and workspace directories are discoverable on sys.path
_current_file_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_file_dir)
_root_dir = os.path.dirname(_backend_dir)
for _p in [_backend_dir, _root_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db, init_db
from app.models import (
    User, Profile, WellnessLog, WellnessGoal, VitalLog,
    MedicineReminder, MedicineLog, Appointment, ChatMessage,
    SymptomLog, MedicalDocument
)
from app.schemas import (
    UserRegister, UserLogin, UserResponse,
    ChatMessageRequest, ChatMessageResponse,
    TriageRequest, TriageResponse,
    WellnessCreateRequest, WellnessUpdateRequest, WellnessGoalsRequest,
    VitalRequest, ProfileRequest, MedicineRequest, AppointmentRequest,
    PrivacyWipeRequest
)
from app import auth
from app import assistant
from app import emergency_triage
from app import wellness
from app import analytics
from app.language_support import TRANSLATIONS_MAP

# Initialize database schema
init_db()

app = FastAPI(
    title="HealthSaathi AI - Advanced Personal Health Copilot API",
    version="2.0.0",
    description="FastAPI REST API powering the HealthSaathi AI Personal Health Companion"
)

# CORS configuration for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# 1. CORE SYSTEM & TRANSLATIONS
# ==============================================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "HealthSaathi AI Copilot",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/translations")
def get_translations():
    # Return complete dictionary for frontend localization
    return TRANSLATIONS_MAP


# ==============================================================================
# 2. AUTHENTICATION & DEMO DATA
# ==============================================================================

@app.post("/api/auth/register")
def register(req: UserRegister, db: Session = Depends(get_db)):
    ok, msg, user = auth.register_user(
        db=db,
        username=req.username,
        password=req.password,
        full_name=req.full_name,
        email=req.email or ""
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email
        }
    }

@app.post("/api/auth/login")
def login(req: UserLogin, db: Session = Depends(get_db)):
    user_dict, msg = auth.authenticate_user(db=db, username=req.username, password=req.password)
    if not user_dict:
        raise HTTPException(status_code=401, detail=msg)
    return {"status": "success", "user": user_dict}

@app.post("/api/auth/demo")
def demo_login(db: Session = Depends(get_db)):
    demo = db.query(User).filter(User.username == "demouser").first()
    if not demo:
        ok, msg, demo = auth.register_user(
            db=db,
            username="demouser",
            password="Demo@Password123",
            full_name="Demo Health User",
            email="demo@healthsaathi.ai"
        )
    return {
        "status": "success",
        "user": {
            "id": demo.id,
            "username": demo.username,
            "full_name": demo.full_name,
            "email": demo.email,
            "token": "demo_session_token"
        }
    }


# ==============================================================================
# 3. SMART CHAT HEALTH ASSISTANT
# ==============================================================================

@app.post("/api/chat")
@app.post("/api/assistant/chat")
def chat_endpoint(req: ChatMessageRequest, db: Session = Depends(get_db)):
    res = assistant.get_assistant_response(
        query=req.message,
        user_id=req.user_id,
        lang=req.lang or "en"
    )
    if req.user_id:
        try:
            # Persist chat history safely
            u_msg = ChatMessage(user_id=req.user_id, role="user", content=req.message)
            a_msg = ChatMessage(user_id=req.user_id, role="assistant", content=res["content"])
            db.add_all([u_msg, a_msg])
            db.commit()
        except Exception:
            db.rollback()
    return res

@app.get("/api/chat/history")
def get_chat_history(user_id: int = Query(...), limit: int = 50, db: Session = Depends(get_db)):
    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.timestamp.asc())
        .limit(limit)
        .all()
    )
    return {
        "history": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M:%S") if m.timestamp else ""
            }
            for m in msgs
        ]
    }

@app.delete("/api/chat/history")
def clear_chat_history(user_id: int = Query(...), db: Session = Depends(get_db)):
    db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    db.commit()
    return {"status": "success", "message": "Conversation history erased"}


# ==============================================================================
# 4. EMERGENCY TRIAGE SYSTEM (3 TIERS)
# ==============================================================================

@app.post("/api/triage")
def triage_endpoint(req: TriageRequest, db: Session = Depends(get_db)):
    result = emergency_triage.evaluate_three_tier_triage(
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
            s_str = ", ".join(req.symptoms or []) if req.symptoms else (req.text_input or "General Triage")
            s_log = SymptomLog(
                user_id=req.user_id,
                symptoms=s_str,
                duration=req.duration or "1 to 3 days",
                severity=req.severity or "Moderate",
                is_emergency=1 if result["tier_level"] == 1 else 0,
                guidance_summary=result["headline"]
            )
            db.add(s_log)
            db.commit()
        except Exception:
            db.rollback()
    return result


# ==============================================================================
# 5. DAILY WELLNESS TRACKER (CRUD)
# ==============================================================================

@app.get("/api/wellness")
def get_wellness(user_id: int = Query(...), days: int = 30, db: Session = Depends(get_db)):
    logs = wellness.get_user_wellness_logs(db=db, user_id=user_id, days=days)
    goal = wellness.get_user_goals(db=db, user_id=user_id)
    return {
        "logs": [
            {
                "id": l.id,
                "log_date": l.log_date,
                "water_ml": l.water_ml,
                "sleep_hours": l.sleep_hours,
                "exercise_mins": l.exercise_mins,
                "exercise_type": l.exercise_type,
                "mood": l.mood,
                "meal_notes": l.meal_notes,
                "notes": l.notes
            }
            for l in logs
        ],
        "goals": {
            "target_water_ml": goal.target_water_ml,
            "target_sleep_hours": goal.target_sleep_hours,
            "target_exercise_mins": goal.target_exercise_mins,
            "target_steps": goal.target_steps
        } if goal else None
    }

@app.post("/api/wellness")
def log_wellness(req: WellnessCreateRequest, db: Session = Depends(get_db)):
    log = wellness.create_wellness_log(
        db=db,
        user_id=req.user_id,
        log_date=req.log_date,
        water_ml=req.water_ml,
        sleep_hours=req.sleep_hours,
        exercise_mins=req.exercise_mins,
        exercise_type=req.exercise_type or "",
        mood=req.mood or "Neutral",
        meal_notes=req.meal_notes or "",
        notes=req.notes or ""
    )
    score_res = wellness.calculate_habit_score(db=db, user_id=req.user_id)
    return {"status": "success", "id": log.id, "habit_score": score_res}

@app.put("/api/wellness/{record_id}")
def update_wellness(record_id: int, req: WellnessUpdateRequest, db: Session = Depends(get_db)):
    log = wellness.update_wellness_log(
        db=db,
        record_id=record_id,
        user_id=req.user_id,
        water_ml=req.water_ml,
        sleep_hours=req.sleep_hours,
        exercise_mins=req.exercise_mins,
        exercise_type=req.exercise_type or "",
        mood=req.mood or "Neutral",
        meal_notes=req.meal_notes or "",
        notes=req.notes or ""
    )
    if not log:
        raise HTTPException(status_code=404, detail="Wellness record not found or unauthorized")
    score_res = wellness.calculate_habit_score(db=db, user_id=req.user_id)
    return {"status": "success", "id": log.id, "habit_score": score_res}

@app.delete("/api/wellness/{record_id}")
def delete_wellness(record_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    ok = wellness.delete_wellness_log(db=db, record_id=record_id, user_id=user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Wellness record not found or unauthorized")
    return {"status": "success"}

@app.post("/api/wellness/goals")
def save_wellness_goals(req: WellnessGoalsRequest, db: Session = Depends(get_db)):
    goal = wellness.get_user_goals(db=db, user_id=req.user_id)
    goal.target_water_ml = req.target_water_ml
    goal.target_sleep_hours = req.target_sleep_hours
    goal.target_exercise_mins = req.target_exercise_mins
    goal.target_steps = req.target_steps
    db.commit()
    return {"status": "success"}


# ==============================================================================
# 6. EXPLAINABLE WELLNESS INTELLIGENCE & INSIGHTS
# ==============================================================================

@app.get("/api/insights")
def get_insights(user_id: int = Query(...), db: Session = Depends(get_db)):
    insights_list = analytics.generate_explainable_insights(db=db, user_id=user_id)
    return {"insights": insights_list}


# ==============================================================================
# 7. DASHBOARD STATS
# ==============================================================================

@app.get("/api/dashboard/stats")
def get_dashboard_stats(user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    vitals = (
        db.query(VitalLog)
        .filter(VitalLog.user_id == user_id)
        .order_by(desc(VitalLog.recorded_at))
        .limit(7)
        .all()
    )
    latest_vital = vitals[0] if vitals else None

    wellness_logs = wellness.get_user_wellness_logs(db=db, user_id=user_id, days=7)
    habit_result = wellness.calculate_habit_score(db=db, user_id=user_id)
    insights_list = analytics.generate_explainable_insights(db=db, user_id=user_id)

    meds_count = db.query(MedicineReminder).filter(MedicineReminder.user_id == user_id, MedicineReminder.is_active == True).count()
    apts_count = db.query(Appointment).filter(Appointment.user_id == user_id).count()
    docs_count = db.query(MedicalDocument).filter(MedicalDocument.user_id == user_id).count()

    anomalies_count = (
        db.query(VitalLog)
        .filter(VitalLog.user_id == user_id, VitalLog.flag_status.in_(["Warning", "Critical"]))
        .count()
    )

    return {
        "profile": {
            "age": profile.age,
            "gender": profile.gender,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "blood_group": profile.blood_group,
            "allergies": profile.allergies,
            "chronic_conditions": profile.chronic_conditions
        } if profile else None,
        "habit_score": habit_result,
        "vitals_count": len(vitals),
        "anomalies_count": anomalies_count,
        "latest_vital": {
            "heart_rate": latest_vital.heart_rate,
            "systolic_bp": latest_vital.systolic_bp,
            "diastolic_bp": latest_vital.diastolic_bp,
            "blood_glucose_mg_dl": latest_vital.blood_glucose_mg_dl,
            "temperature_f": latest_vital.temperature_f
        } if latest_vital else None,
        "recent_vitals": [
            {
                "id": v.id,
                "recorded_at": v.recorded_at.strftime("%Y-%m-%d %H:%M") if v.recorded_at else "",
                "systolic_bp": v.systolic_bp,
                "diastolic_bp": v.diastolic_bp,
                "heart_rate": v.heart_rate,
                "blood_glucose_mg_dl": v.blood_glucose_mg_dl
            }
            for v in vitals
        ],
        "active_medicines_count": meds_count,
        "appointments_count": apts_count,
        "documents_count": docs_count,
        "wellness_logs": [
            {
                "id": w.id,
                "log_date": w.log_date,
                "water_ml": w.water_ml,
                "sleep_hours": w.sleep_hours,
                "exercise_mins": w.exercise_mins
            }
            for w in wellness_logs
        ],
        "smart_insights": insights_list
    }


# ==============================================================================
# 8. PROFILE & PRIVACY WIPE
# ==============================================================================

@app.get("/api/profile")
def get_profile(user_id: int = Query(...), db: Session = Depends(get_db)):
    prof = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not prof:
        return {"profile": None, "bmi": None}

    bmi_info = None
    if prof.height_cm and prof.weight_kg and prof.height_cm > 0:
        h_m = prof.height_cm / 100.0
        val = round(prof.weight_kg / (h_m * h_m), 1)
        cat = "Underweight" if val < 18.5 else "Normal weight" if val < 25 else "Overweight" if val < 30 else "Obese"
        bmi_info = {"bmi": val, "category": cat}

    return {
        "profile": {
            "age": prof.age,
            "gender": prof.gender,
            "height_cm": prof.height_cm,
            "weight_kg": prof.weight_kg,
            "blood_group": prof.blood_group,
            "emergency_contact_name": prof.emergency_contact_name,
            "emergency_contact_phone": prof.emergency_contact_phone,
            "allergies": prof.allergies,
            "chronic_conditions": prof.chronic_conditions,
            "medications_summary": prof.medications_summary
        },
        "bmi": bmi_info
    }

@app.post("/api/profile")
def save_profile(req: ProfileRequest, db: Session = Depends(get_db)):
    prof = db.query(Profile).filter(Profile.user_id == req.user_id).first()
    if not prof:
        prof = Profile(user_id=req.user_id)
        db.add(prof)

    prof.age = req.age
    prof.gender = req.gender
    prof.height_cm = req.height_cm
    prof.weight_kg = req.weight_kg
    prof.blood_group = req.blood_group
    prof.emergency_contact_name = req.emergency_contact_name
    prof.emergency_contact_phone = req.emergency_contact_phone
    prof.allergies = req.allergies
    prof.chronic_conditions = req.chronic_conditions
    prof.medications_summary = req.medications_summary
    db.commit()

    bmi_info = None
    if req.height_cm and req.weight_kg and req.height_cm > 0:
        h_m = req.height_cm / 100.0
        val = round(req.weight_kg / (h_m * h_m), 1)
        cat = "Underweight" if val < 18.5 else "Normal weight" if val < 25 else "Overweight" if val < 30 else "Obese"
        bmi_info = {"bmi": val, "category": cat}

    return {"status": "success", "bmi": bmi_info}

@app.post("/api/privacy/wipe")
def wipe_user_records(req: PrivacyWipeRequest, db: Session = Depends(get_db)):
    uid = req.user_id
    db.query(WellnessLog).filter(WellnessLog.user_id == uid).delete()
    db.query(VitalLog).filter(VitalLog.user_id == uid).delete()
    db.query(MedicineReminder).filter(MedicineReminder.user_id == uid).delete()
    db.query(MedicineLog).filter(MedicineLog.user_id == uid).delete()
    db.query(Appointment).filter(Appointment.user_id == uid).delete()
    db.query(ChatMessage).filter(ChatMessage.user_id == uid).delete()
    db.query(SymptomLog).filter(SymptomLog.user_id == uid).delete()
    db.query(MedicalDocument).filter(MedicalDocument.user_id == uid).delete()
    db.commit()
    return {"status": "success", "message": "All personal health records permanently deleted"}


# ==============================================================================
# 9. VITALS
# ==============================================================================

@app.get("/api/vitals")
def get_vitals(user_id: int = Query(...), limit: int = 50, db: Session = Depends(get_db)):
    rows = (
        db.query(VitalLog)
        .filter(VitalLog.user_id == user_id)
        .order_by(desc(VitalLog.recorded_at))
        .limit(limit)
        .all()
    )
    return {
        "vitals": [
            {
                "id": r.id,
                "recorded_at": r.recorded_at.strftime("%Y-%m-%d %H:%M") if r.recorded_at else "",
                "systolic_bp": r.systolic_bp,
                "diastolic_bp": r.diastolic_bp,
                "heart_rate": r.heart_rate,
                "temperature_f": r.temperature_f,
                "weight_kg": r.weight_kg,
                "blood_glucose_mg_dl": r.blood_glucose_mg_dl,
                "glucose_context": r.glucose_context,
                "flag_status": r.flag_status,
                "notes": r.notes
            }
            for r in rows
        ]
    }

@app.post("/api/vitals")
def log_vitals(req: VitalRequest, db: Session = Depends(get_db)):
    # Physiological flags
    flag_status = "Normal"
    flags = []
    if req.systolic_bp and req.systolic_bp >= 140:
        flags.append("High Systolic BP")
        flag_status = "Warning"
    if req.diastolic_bp and req.diastolic_bp >= 90:
        flags.append("High Diastolic BP")
        flag_status = "Warning"
    if req.heart_rate and (req.heart_rate > 100 or req.heart_rate < 55):
        flags.append("Abnormal Heart Rate")
        flag_status = "Warning"

    combined_notes = req.notes or ""
    if flags:
        combined_notes = f"{combined_notes} [{' | '.join(flags)}]".strip()

    v = VitalLog(
        user_id=req.user_id,
        systolic_bp=req.systolic_bp,
        diastolic_bp=req.diastolic_bp,
        heart_rate=req.heart_rate,
        temperature_f=req.temperature_f,
        weight_kg=req.weight_kg,
        blood_glucose_mg_dl=req.blood_glucose_mg_dl,
        glucose_context=req.glucose_context,
        flag_status=flag_status,
        notes=combined_notes
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return {"status": "success", "id": v.id, "flag_status": flag_status}

@app.delete("/api/vitals/{vital_id}")
def delete_vital(vital_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    v = db.query(VitalLog).filter(VitalLog.id == vital_id, VitalLog.user_id == user_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(v)
    db.commit()
    return {"status": "success"}


# ==============================================================================
# 10. MEDICINES & APPOINTMENTS
# ==============================================================================

@app.get("/api/medicines")
def get_medicines(user_id: int = Query(...), db: Session = Depends(get_db)):
    rows = db.query(MedicineReminder).filter(MedicineReminder.user_id == user_id).all()
    today_dt = date.today()
    taken_med_ids = {
        m.reminder_id for m in db.query(MedicineLog).filter(
            MedicineLog.user_id == user_id, MedicineLog.log_date == today_dt
        ).all()
    }
    return {
        "medicines": [
            {
                "id": r.id,
                "medicine_name": r.medicine_name,
                "dosage": r.dosage,
                "schedule_timing": r.schedule_timing,
                "time_str": r.time_str,
                "instructions": r.instructions,
                "is_active": r.is_active,
                "taken_today": r.id in taken_med_ids
            }
            for r in rows
        ]
    }

@app.post("/api/medicines")
def add_medicine(req: MedicineRequest, db: Session = Depends(get_db)):
    m = MedicineReminder(
        user_id=req.user_id,
        medicine_name=req.medicine_name,
        dosage=req.dosage,
        schedule_timing=req.schedule_timing,
        time_str=req.time_str,
        instructions=req.instructions or ""
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"status": "success", "id": m.id}

@app.post("/api/medicines/{med_id}/toggle")
def toggle_medicine(med_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    today_dt = date.today()
    existing = db.query(MedicineLog).filter(
        MedicineLog.user_id == user_id,
        MedicineLog.reminder_id == med_id,
        MedicineLog.log_date == today_dt
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"status": "success", "taken": False}
    else:
        new_log = MedicineLog(user_id=user_id, reminder_id=med_id, log_date=today_dt)
        db.add(new_log)
        db.commit()
        return {"status": "success", "taken": True}

@app.delete("/api/medicines/{med_id}")
def delete_medicine(med_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    m = db.query(MedicineReminder).filter(MedicineReminder.id == med_id, MedicineReminder.user_id == user_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Medicine not found")
    db.delete(m)
    db.commit()
    return {"status": "success"}

@app.get("/api/appointments")
def get_appointments(user_id: int = Query(...), db: Session = Depends(get_db)):
    rows = db.query(Appointment).filter(Appointment.user_id == user_id).order_by(Appointment.appointment_date.asc()).all()
    return {
        "appointments": [
            {
                "id": a.id,
                "doctor_name": a.doctor_name,
                "specialty": a.specialty,
                "clinic_hospital": a.clinic_hospital,
                "appointment_date": a.appointment_date.strftime("%Y-%m-%d"),
                "appointment_time": a.appointment_time,
                "reason": a.reason,
                "phone": a.phone,
                "status": a.status
            }
            for a in rows
        ]
    }

@app.post("/api/appointments")
def book_appointment(req: AppointmentRequest, db: Session = Depends(get_db)):
    a_dt = datetime.strptime(req.appointment_date, "%Y-%m-%d").date()
    apt = Appointment(
        user_id=req.user_id,
        doctor_name=req.doctor_name,
        specialty=req.specialty,
        clinic_hospital=req.clinic_hospital,
        appointment_date=a_dt,
        appointment_time=req.appointment_time,
        reason=req.reason or "",
        phone=req.phone or ""
    )
    db.add(apt)
    db.commit()
    db.refresh(apt)
    return {"status": "success", "id": apt.id}

@app.delete("/api/appointments/{apt_id}")
def delete_appointment(apt_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id, Appointment.user_id == user_id).first()
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(apt)
    db.commit()
    return {"status": "success"}


# ==============================================================================
# 11. DOCUMENT STORAGE VAULT & PDF REPORTS
# ==============================================================================

@app.get("/api/documents")
def get_documents(user_id: int = Query(...), db: Session = Depends(get_db)):
    docs = db.query(MedicalDocument).filter(MedicalDocument.user_id == user_id).order_by(desc(MedicalDocument.upload_date)).all()
    return {
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "category": d.category,
                "report_date": d.report_date,
                "doctor_or_lab": d.doctor_or_lab,
                "file_name": d.file_name,
                "file_size_kb": d.file_size_kb,
                "file_type": d.file_type,
                "notes": d.notes
            }
            for d in docs
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
