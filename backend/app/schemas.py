"""
backend/app/schemas.py - Pydantic Request & Response Validation Schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr


# ==============================================================================
# AUTH & USER SCHEMAS
# ==============================================================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = ""

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str] = ""

    class Config:
        from_attributes = True


# ==============================================================================
# PROFILE SCHEMAS
# ==============================================================================

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


# ==============================================================================
# CHAT ASSISTANT SCHEMAS
# ==============================================================================

class ChatMessageRequest(BaseModel):
    user_id: Optional[int] = None
    message: str = Field(..., min_length=1)
    lang: Optional[str] = "en"  # "en", "te", "te-roman"

class ChatMessageResponse(BaseModel):
    category: str
    rule_id: str
    title: str
    content: str
    matched_rule: str
    is_emergency: bool
    follow_ups: List[str] = []


# ==============================================================================
# EMERGENCY TRIAGE SCHEMAS
# ==============================================================================

class TriageRequest(BaseModel):
    user_id: Optional[int] = None
    symptoms: Optional[List[str]] = []
    text_input: Optional[str] = ""
    severity: Optional[str] = "Moderate"
    duration: Optional[str] = "1 to 3 days"
    age: Optional[int] = None
    gender: Optional[str] = None
    lang: Optional[str] = "en"

class TriageResponse(BaseModel):
    tier: str
    tier_level: int
    badge_color: str
    headline: str
    call_to_action: str
    emergency_numbers: List[str]
    category: str
    reasons: List[str]
    urgent_actions: List[str]
    limitation: str


# ==============================================================================
# WELLNESS TRACKER SCHEMAS
# ==============================================================================

class WellnessCreateRequest(BaseModel):
    user_id: int
    log_date: str  # YYYY-MM-DD
    water_ml: int = Field(0, ge=0)
    sleep_hours: float = Field(0.0, ge=0.0, le=24.0)
    exercise_mins: int = Field(0, ge=0)
    exercise_type: Optional[str] = ""
    mood: Optional[str] = "Neutral"
    meal_notes: Optional[str] = ""
    notes: Optional[str] = ""

class WellnessUpdateRequest(BaseModel):
    user_id: int
    water_ml: int = Field(0, ge=0)
    sleep_hours: float = Field(0.0, ge=0.0, le=24.0)
    exercise_mins: int = Field(0, ge=0)
    exercise_type: Optional[str] = ""
    mood: Optional[str] = "Neutral"
    meal_notes: Optional[str] = ""
    notes: Optional[str] = ""

class WellnessGoalsRequest(BaseModel):
    user_id: int
    target_water_ml: int = Field(2500, ge=500, le=8000)
    target_sleep_hours: float = Field(7.5, ge=4.0, le=14.0)
    target_exercise_mins: int = Field(30, ge=0, le=300)
    target_steps: int = Field(8000, ge=0, le=50000)


# ==============================================================================
# VITALS TRACKER SCHEMAS
# ==============================================================================

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


# ==============================================================================
# MEDICINES & APPOINTMENTS
# ==============================================================================

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

class PrivacyWipeRequest(BaseModel):
    user_id: int
