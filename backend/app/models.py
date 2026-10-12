"""
backend/app/models.py - SQLAlchemy ORM Models
Defines relational mappings for users, profiles, wellness tracking, vitals,
appointments, prescriptions, and chat history.
Aligns cleanly with existing SQLite database schemas.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Text, Date, DateTime,
    ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
try:
    from backend.app.database import Base
except ImportError:
    from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    salt = Column(String(64), nullable=False)
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wellness_logs = relationship("WellnessLog", back_populates="user", cascade="all, delete-orphan")
    wellness_goal = relationship("WellnessGoal", back_populates="user", uselist=False, cascade="all, delete-orphan")
    vitals = relationship("VitalLog", back_populates="user", cascade="all, delete-orphan")
    medicines = relationship("MedicineReminder", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    symptoms = relationship("SymptomLog", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("MedicalDocument", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(30), nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    blood_group = Column(String(10), nullable=True)
    emergency_contact_name = Column(String(150), nullable=True)
    emergency_contact_phone = Column(String(50), nullable=True)
    allergies = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)
    medications_summary = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class WellnessLog(Base):
    __tablename__ = "wellness_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    log_date = Column(String(20), nullable=False, index=True)  # YYYY-MM-DD
    water_ml = Column(Integer, default=0)
    sleep_hours = Column(Float, default=0.0)
    exercise_mins = Column(Integer, default=0)
    exercise_type = Column(String(100), default="")
    mood = Column(String(50), default="Neutral")
    meal_notes = Column(Text, default="")
    notes = Column(Text, default="")

    user = relationship("User", back_populates="wellness_logs")


class WellnessGoal(Base):
    __tablename__ = "wellness_goals"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    target_water_ml = Column(Integer, default=2500)
    target_sleep_hours = Column(Float, default=7.5)
    target_exercise_mins = Column(Integer, default=30)
    target_steps = Column(Integer, default=8000)

    user = relationship("User", back_populates="wellness_goal")


class VitalLog(Base):
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    temperature_f = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    blood_glucose_mg_dl = Column(Integer, nullable=True)
    glucose_context = Column(String(50), default="Random")
    flag_status = Column(String(50), default="Normal")
    notes = Column(Text, default="")

    user = relationship("User", back_populates="vitals")


class MedicineReminder(Base):
    __tablename__ = "medicine_reminders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    medicine_name = Column(String(150), nullable=False)
    dosage = Column(String(100), nullable=False)
    schedule_timing = Column(String(100), nullable=False)
    time_str = Column(String(20), nullable=False)
    instructions = Column(Text, default="")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="medicines")


class MedicineLog(Base):
    __tablename__ = "medicine_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reminder_id = Column(Integer, ForeignKey("medicine_reminders.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False, default=date.today)
    taken_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="Completed")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_name = Column(String(150), nullable=False)
    specialty = Column(String(100), nullable=True)
    clinic_hospital = Column(String(200), nullable=True)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(String(20), nullable=False)
    notes = Column(Text, default="")
    status = Column(String(50), default="Scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="appointments")


class ChatMessage(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")


class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    logged_at = Column(DateTime, default=datetime.utcnow)
    symptoms = Column(Text, nullable=False)
    duration = Column(String(100), default="1 to 3 days")
    severity = Column(String(50), default="Moderate")
    is_emergency = Column(Integer, default=0)
    guidance_summary = Column(Text, default="")

    user = relationship("User", back_populates="symptoms")


class MedicalDocument(Base):
    __tablename__ = "medical_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    report_date = Column(Date, nullable=False)
    doctor_or_lab = Column(String(200), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_kb = Column(Float, default=0.0)
    file_type = Column(String(20), default="PDF")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")
