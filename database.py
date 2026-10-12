"""
database.py - SQLite Database Layer for AI Powered Personal Health Copilot
Ensures parameterized queries, user isolation, data persistence, and cascading cleanup.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "health_copilot.db")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db_connection():
    """Returns an active SQLite connection with row factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initializes all database tables with appropriate schemas and indexes."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Health Profiles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        age INTEGER,
        gender TEXT,
        height_cm REAL,
        weight_kg REAL,
        blood_group TEXT,
        emergency_contact_name TEXT,
        emergency_contact_phone TEXT,
        allergies TEXT,
        chronic_conditions TEXT,
        medications_summary TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 3. Vitals Tracker table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vitals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recorded_at TIMESTAMP NOT NULL,
        systolic_bp INTEGER,
        diastolic_bp INTEGER,
        heart_rate INTEGER,
        temperature_f REAL,
        weight_kg REAL,
        blood_glucose_mg_dl REAL,
        glucose_context TEXT,
        notes TEXT,
        flag_status TEXT DEFAULT 'Normal',
        flag_reasons TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 4. Daily Wellness Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wellness_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        log_date DATE NOT NULL,
        water_ml INTEGER DEFAULT 0,
        sleep_hours REAL DEFAULT 0.0,
        exercise_mins INTEGER DEFAULT 0,
        exercise_type TEXT,
        mood TEXT,
        meal_notes TEXT,
        notes TEXT,
        UNIQUE (user_id, log_date),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 5. Wellness Goals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wellness_goals (
        user_id INTEGER PRIMARY KEY,
        target_water_ml INTEGER DEFAULT 2500,
        target_sleep_hours REAL DEFAULT 8.0,
        target_exercise_mins INTEGER DEFAULT 30,
        target_steps INTEGER DEFAULT 8000,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 6. Medicine Reminders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicine_reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        schedule_timing TEXT NOT NULL,
        time_str TEXT NOT NULL,
        instructions TEXT,
        start_date DATE,
        end_date DATE,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 7. Medicine Completion Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicine_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reminder_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        log_date DATE NOT NULL,
        taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Completed',
        UNIQUE (reminder_id, log_date),
        FOREIGN KEY (reminder_id) REFERENCES medicine_reminders (id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 8. Doctor Appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doctor_name TEXT NOT NULL,
        clinic_hospital TEXT,
        specialty TEXT,
        appointment_date DATE NOT NULL,
        appointment_time TEXT NOT NULL,
        status TEXT DEFAULT 'Scheduled',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 9. Symptom Checker Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS symptom_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        logged_at TIMESTAMP NOT NULL,
        symptoms TEXT NOT NULL,
        duration TEXT NOT NULL,
        severity TEXT NOT NULL,
        is_emergency INTEGER DEFAULT 0,
        guidance_summary TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 10. AI Chat Assistant History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # 11. Stored Medical Documents & Lab Reports table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        report_date DATE NOT NULL,
        doctor_or_lab TEXT,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size_kb REAL DEFAULT 0,
        file_type TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()


# ==============================================================================
# USER & AUTHENTICATION CRUD
# ==============================================================================

def create_user(username: str, password_hash: str, salt: str, full_name: str, email: Optional[str] = None) -> Optional[int]:
    """Registers a new user and returns their new ID, or None if username exists."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt, full_name, email) VALUES (?, ?, ?, ?, ?)",
            (username.strip().lower(), password_hash, salt, full_name.strip(), email.strip() if email else None)
        )
        user_id = cursor.lastrowid
        # Initialize default goals
        cursor.execute(
            "INSERT OR IGNORE INTO wellness_goals (user_id, target_water_ml, target_sleep_hours, target_exercise_mins) VALUES (?, ?, ?, ?)",
            (user_id, 2500, 8.0, 30)
        )
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    """Fetch user record by unique username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return row


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    """Fetch user record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def delete_user(user_id: int) -> bool:
    """Permanently delete user and all associated health records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    # Clean up physical uploads directory for user
    import shutil
    user_upload_dir = os.path.join(UPLOAD_DIR, f"user_{user_id}")
    if os.path.exists(user_upload_dir):
        try:
            shutil.rmtree(user_upload_dir)
        except Exception:
            pass

    return rows_affected > 0


# ==============================================================================
# HEALTH PROFILE CRUD
# ==============================================================================

def get_profile(user_id: int) -> Optional[sqlite3.Row]:
    """Fetch health profile for a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def save_profile(user_id: int, age: Optional[int], gender: Optional[str],
                 height_cm: Optional[float], weight_kg: Optional[float],
                 blood_group: Optional[str], emergency_contact_name: Optional[str],
                 emergency_contact_phone: Optional[str], allergies: Optional[str],
                 chronic_conditions: Optional[str], medications_summary: Optional[str]):
    """Insert or update health profile."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO profiles (
        user_id, age, gender, height_cm, weight_kg, blood_group,
        emergency_contact_name, emergency_contact_phone, allergies,
        chronic_conditions, medications_summary, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(user_id) DO UPDATE SET
        age = excluded.age,
        gender = excluded.gender,
        height_cm = excluded.height_cm,
        weight_kg = excluded.weight_kg,
        blood_group = excluded.blood_group,
        emergency_contact_name = excluded.emergency_contact_name,
        emergency_contact_phone = excluded.emergency_contact_phone,
        allergies = excluded.allergies,
        chronic_conditions = excluded.chronic_conditions,
        medications_summary = excluded.medications_summary,
        updated_at = CURRENT_TIMESTAMP;
    """, (
        user_id, age, gender, height_cm, weight_kg, blood_group,
        emergency_contact_name, emergency_contact_phone, allergies,
        chronic_conditions, medications_summary
    ))
    conn.commit()
    conn.close()


def clear_profile(user_id: int):
    """Clear health profile information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ==============================================================================
# VITALS TRACKER CRUD
# ==============================================================================

def log_vital(user_id: int, systolic_bp: Optional[int], diastolic_bp: Optional[int],
              heart_rate: Optional[int], temperature_f: Optional[float],
              weight_kg: Optional[float], blood_glucose_mg_dl: Optional[float],
              glucose_context: Optional[str], notes: Optional[str],
              flag_status: str = "Normal", flag_reasons: Optional[str] = None,
              recorded_at: Optional[datetime] = None) -> int:
    """Save a new vital sign measurement."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = recorded_at.strftime("%Y-%m-%d %H:%M:%S") if recorded_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO vitals (
        user_id, recorded_at, systolic_bp, diastolic_bp, heart_rate,
        temperature_f, weight_kg, blood_glucose_mg_dl, glucose_context,
        notes, flag_status, flag_reasons
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, ts, systolic_bp, diastolic_bp, heart_rate,
        temperature_f, weight_kg, blood_glucose_mg_dl, glucose_context,
        notes, flag_status, flag_reasons
    ))
    vital_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return vital_id


def get_vitals(user_id: int, limit: int = 100) -> List[sqlite3.Row]:
    """Retrieve historical vitals ordered by timestamp descending."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM vitals WHERE user_id = ? ORDER BY recorded_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_latest_vital(user_id: int) -> Optional[sqlite3.Row]:
    """Retrieve the most recently recorded vital entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM vitals WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def delete_vital(vital_id: int, user_id: int) -> bool:
    """Delete a specific vitals record ensuring user ownership."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vitals WHERE id = ? AND user_id = ?", (vital_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ==============================================================================
# DAILY WELLNESS LOGS & GOALS CRUD
# ==============================================================================

def log_wellness(user_id: int, log_date: date, water_ml: int, sleep_hours: float,
                 exercise_mins: int, exercise_type: Optional[str] = None,
                 mood: Optional[str] = None, meal_notes: Optional[str] = None,
                 notes: Optional[str] = None):
    """Upsert daily wellness log for given date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO wellness_logs (
        user_id, log_date, water_ml, sleep_hours, exercise_mins,
        exercise_type, mood, meal_notes, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(user_id, log_date) DO UPDATE SET
        water_ml = excluded.water_ml,
        sleep_hours = excluded.sleep_hours,
        exercise_mins = excluded.exercise_mins,
        exercise_type = excluded.exercise_type,
        mood = excluded.mood,
        meal_notes = excluded.meal_notes,
        notes = excluded.notes;
    """, (
        user_id, log_date.strftime("%Y-%m-%d"), water_ml, sleep_hours,
        exercise_mins, exercise_type, mood, meal_notes, notes
    ))
    conn.commit()
    conn.close()


def get_wellness_for_date(user_id: int, log_date: date) -> Optional[sqlite3.Row]:
    """Fetch wellness record for a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM wellness_logs WHERE user_id = ? AND log_date = ?",
        (user_id, log_date.strftime("%Y-%m-%d"))
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_wellness_logs(user_id: int, days: int = 30) -> List[sqlite3.Row]:
    """Fetch wellness records from the last N days sorted chronologically."""
    conn = get_db_connection()
    cursor = conn.cursor()
    since_date = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT * FROM wellness_logs WHERE user_id = ? AND log_date >= ? ORDER BY log_date ASC",
        (user_id, since_date)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_wellness_goals(user_id: int) -> Dict[str, Any]:
    """Fetch user wellness goals, returning sensible defaults if not set."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM wellness_goals WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "target_water_ml": 2500,
        "target_sleep_hours": 8.0,
        "target_exercise_mins": 30,
        "target_steps": 8000
    }


def save_wellness_goals(user_id: int, target_water_ml: int, target_sleep_hours: float,
                        target_exercise_mins: int, target_steps: int = 8000):
    """Save user wellness goals."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO wellness_goals (user_id, target_water_ml, target_sleep_hours, target_exercise_mins, target_steps)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        target_water_ml = excluded.target_water_ml,
        target_sleep_hours = excluded.target_sleep_hours,
        target_exercise_mins = excluded.target_exercise_mins,
        target_steps = excluded.target_steps;
    """, (user_id, target_water_ml, target_sleep_hours, target_exercise_mins, target_steps))
    conn.commit()
    conn.close()


def update_wellness_log(log_id: int, user_id: int, water_ml: int, sleep_hours: float,
                        exercise_mins: int, exercise_type: Optional[str] = None,
                        mood: Optional[str] = None, meal_notes: Optional[str] = None,
                        notes: Optional[str] = None) -> bool:
    """Update an existing wellness log entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE wellness_logs 
    SET water_ml = ?, sleep_hours = ?, exercise_mins = ?,
        exercise_type = ?, mood = ?, meal_notes = ?, notes = ?
    WHERE id = ? AND user_id = ?
    """, (water_ml, sleep_hours, exercise_mins, exercise_type, mood, meal_notes, notes, log_id, user_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_wellness_log(log_id: int, user_id: int) -> bool:
    """Delete a specific wellness log entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wellness_logs WHERE id = ? AND user_id = ?", (log_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def wipe_user_data(user_id: int) -> bool:
    """Permanently delete all personal health records for a user adhering to privacy rights."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vitals WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM wellness_logs WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM wellness_goals WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM medicine_reminders WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM medicine_logs WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM appointments WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM symptom_logs WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM medical_documents WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def add_medicine_reminder(user_id: int, medicine_name: str, dosage: str,
                          schedule_timing: str, time_str: str,
                          instructions: Optional[str] = None,
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None) -> int:
    """Add a new medication reminder entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO medicine_reminders (
        user_id, medicine_name, dosage, schedule_timing, time_str,
        instructions, start_date, end_date, is_active
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        user_id, medicine_name.strip(), dosage.strip(), schedule_timing.strip(),
        time_str.strip(), instructions.strip() if instructions else None,
        start_date.strftime("%Y-%m-%d") if start_date else None,
        end_date.strftime("%Y-%m-%d") if end_date else None
    ))
    med_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return med_id


def get_medicine_reminders(user_id: int, active_only: bool = True) -> List[sqlite3.Row]:
    """Retrieve medication reminders."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if active_only:
        cursor.execute(
            "SELECT * FROM medicine_reminders WHERE user_id = ? AND is_active = 1 ORDER BY time_str ASC",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT * FROM medicine_reminders WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_medicine_reminder(reminder_id: int, user_id: int) -> bool:
    """Delete a medication reminder."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicine_reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def mark_medicine_taken(reminder_id: int, user_id: int, log_date: date):
    """Mark a medication as taken on a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO medicine_logs (reminder_id, user_id, log_date, taken_at, status)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'Completed')
    """, (reminder_id, user_id, log_date.strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()


def unmark_medicine_taken(reminder_id: int, user_id: int, log_date: date):
    """Remove completion mark for given medication on date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM medicine_logs WHERE reminder_id = ? AND user_id = ? AND log_date = ?",
        (reminder_id, user_id, log_date.strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()


def get_medicine_logs_for_date(user_id: int, log_date: date) -> List[int]:
    """Return list of reminder_ids completed on the specified date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT reminder_id FROM medicine_logs WHERE user_id = ? AND log_date = ?",
        (user_id, log_date.strftime("%Y-%m-%d"))
    )
    rows = cursor.fetchall()
    conn.close()
    return [row["reminder_id"] for row in rows]


# ==============================================================================
# DOCTOR APPOINTMENTS CRUD
# ==============================================================================

def add_appointment(user_id: int, doctor_name: str, clinic_hospital: Optional[str],
                    specialty: Optional[str], appointment_date: date,
                    appointment_time: str, notes: Optional[str] = None) -> int:
    """Schedule a new doctor consultation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO appointments (
        user_id, doctor_name, clinic_hospital, specialty,
        appointment_date, appointment_time, notes, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Scheduled')
    """, (
        user_id, doctor_name.strip(), clinic_hospital.strip() if clinic_hospital else None,
        specialty.strip() if specialty else None, appointment_date.strftime("%Y-%m-%d"),
        appointment_time.strip(), notes.strip() if notes else None
    ))
    apt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return apt_id


def get_appointments(user_id: int, status_filter: Optional[str] = None) -> List[sqlite3.Row]:
    """Fetch appointments with optional status filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute(
            "SELECT * FROM appointments WHERE user_id = ? AND status = ? ORDER BY appointment_date ASC, appointment_time ASC",
            (user_id, status_filter)
        )
    else:
        cursor.execute(
            "SELECT * FROM appointments WHERE user_id = ? ORDER BY appointment_date ASC, appointment_time ASC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_appointment_status(appointment_id: int, user_id: int, status: str) -> bool:
    """Update appointment status (e.g. Scheduled, Completed, Cancelled)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE appointments SET status = ? WHERE id = ? AND user_id = ?",
        (status, appointment_id, user_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_appointment(appointment_id: int, user_id: int) -> bool:
    """Delete an appointment entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ? AND user_id = ?", (appointment_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ==============================================================================
# SYMPTOM CHECKER LOGS CRUD
# ==============================================================================

def log_symptom(user_id: int, symptoms: str, duration: str, severity: str,
                is_emergency: int, guidance_summary: str) -> int:
    """Save symptom assessment session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO symptom_logs (user_id, logged_at, symptoms, duration, severity, is_emergency, guidance_summary)
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
    """, (user_id, symptoms, duration, severity, is_emergency, guidance_summary))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_symptom_logs(user_id: int, limit: int = 20) -> List[sqlite3.Row]:
    """Fetch recent symptom check logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM symptom_logs WHERE user_id = ? ORDER BY logged_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ==============================================================================
# CHAT ASSISTANT HISTORY CRUD
# ==============================================================================

def save_chat_message(user_id: int, role: str, content: str):
    """Store conversation exchange."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    conn.commit()
    conn.close()


def get_chat_history(user_id: int, limit: int = 40) -> List[sqlite3.Row]:
    """Retrieve recent chat history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_chat_history(user_id: int):
    """Clear conversation history for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ==============================================================================
# MEDICAL DOCUMENTS & REPORT UPLOADS CRUD
# ==============================================================================

def get_user_upload_dir(user_id: int) -> str:
    """Returns and ensures the user's isolated upload directory exists."""
    user_dir = os.path.join(UPLOAD_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def add_medical_document(
    user_id: int,
    title: str,
    category: str,
    report_date: Any,
    doctor_or_lab: Optional[str],
    file_name: str,
    file_path: Optional[str] = None,
    file_size_kb: Optional[float] = None,
    file_type: Optional[str] = None,
    notes: Optional[str] = None,
    file_bytes: Optional[bytes] = None
) -> int:
    """Records an uploaded medical document in SQLite, optionally writing bytes to user storage."""
    if file_bytes is not None:
        user_upload_dir = get_user_upload_dir(user_id)
        safe_time = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_clean = "".join(c for c in file_name if c.isalnum() or c in (".", "_", "-")).strip()
        saved_filename = f"doc_{safe_time}_{safe_clean}"
        file_path = os.path.join(user_upload_dir, saved_filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        file_size_kb = round(len(file_bytes) / 1024.0, 1)
        if not file_type:
            ext = os.path.splitext(file_name)[1].lower()
            file_type = ext.replace(".", "").upper() or "DOC"

    if file_path is None:
        file_path = ""
    if file_size_kb is None:
        file_size_kb = 0.0
    if file_type is None:
        file_type = "DOC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO medical_documents
        (user_id, title, category, report_date, doctor_or_lab, file_name, file_path, file_size_kb, file_type, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            title.strip(),
            category.strip(),
            str(report_date),
            doctor_or_lab.strip() if doctor_or_lab else None,
            file_name.strip(),
            file_path,
            round(float(file_size_kb), 1),
            file_type.upper().strip(),
            notes.strip() if notes else None
        )
    )
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def get_medical_documents(user_id: int, category_filter: Optional[str] = None) -> List[sqlite3.Row]:
    """Retrieves all medical documents for a user, optionally filtered by category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if category_filter and category_filter not in ("All", "All Categories", "All Reports", "అన్నీ"):
        cursor.execute(
            "SELECT * FROM medical_documents WHERE user_id = ? AND category = ? ORDER BY report_date DESC, id DESC",
            (user_id, category_filter)
        )
    else:
        cursor.execute(
            "SELECT * FROM medical_documents WHERE user_id = ? ORDER BY report_date DESC, id DESC",
            (user_id,)
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_medical_document_by_id(doc_id: int, user_id: int) -> Optional[sqlite3.Row]:
    """Retrieves a single medical document with user isolation check."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM medical_documents WHERE id = ? AND user_id = ?",
        (doc_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def delete_medical_document(doc_id: int, user_id: int) -> bool:
    """Deletes document record and physically removes the stored file from disk."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT file_path FROM medical_documents WHERE id = ? AND user_id = ?",
        (doc_id, user_id)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    file_path = row["file_path"]
    cursor.execute(
        "DELETE FROM medical_documents WHERE id = ? AND user_id = ?",
        (doc_id, user_id)
    )
    conn.commit()
    conn.close()

    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
    return True


# ==============================================================================
# DEMO DATA SEEDER (Instant Evaluation & Rich Testing)
# ==============================================================================

def seed_demo_data(user_id: int):
    """Populates comprehensive realistic demo data for the given user."""
    # 1. Profile
    save_profile(
        user_id=user_id,
        age=34,
        gender="Male",
        height_cm=175.0,
        weight_kg=72.5,
        blood_group="O+",
        emergency_contact_name="Ravi Kumar (Brother)",
        emergency_contact_phone="+91 98765 43210",
        allergies="Penicillin, Pollen",
        chronic_conditions="Mild Seasonal Allergies",
        medications_summary="Daily Multivitamin, Cetirizine as needed"
    )

    # 2. Goals
    save_wellness_goals(
        user_id=user_id,
        target_water_ml=2750,
        target_sleep_hours=7.5,
        target_exercise_mins=35,
        target_steps=9000
    )

    # 3. 14 Days of Daily Wellness Logs
    today = date.today()
    wellness_sample = [
        (2500, 7.5, 30, "Brisk Walking", "Energetic", "Oats, Dal, Rotis, Mixed greens"),
        (2750, 8.0, 40, "Morning Yoga", "Calm", "Idli with sambar, Salad, Grilled paneer"),
        (2250, 6.5, 20, "Stretching", "Tired", "Rice with dal, Vegetable curry"),
        (3000, 7.8, 45, "Brisk Walking", "Great", "Sprouts salad, Millet upma, Curd"),
        (2600, 7.2, 35, "Cycling", "Focused", "Brown rice, Rajma, Spinach curry"),
        (2400, 7.0, 25, "Evening Walk", "Normal", "Roti, Palak paneer, Papaya bowl"),
        (2800, 8.2, 50, "Yoga & Meditation", "Refreshed", "Vegetable soup, Steamed sprouts"),
        (2500, 7.4, 30, "Light Jogging", "Active", "Upma with chutney, Curd rice"),
        (2900, 7.6, 40, "Badminton", "High Energy", "Dosa with vegetable kurma, Fresh apple"),
        (2300, 6.8, 20, "Evening Walk", "Busy", "Quick vegetable wrap, Buttermilk"),
        (2700, 7.5, 35, "Yoga & Pranayama", "Peaceful", "Khichdi with mixed veggies, Cucumber"),
        (3100, 8.0, 45, "Swimming", "Invigorated", "Boiled eggs, Millet porridge, Almonds"),
        (2650, 7.3, 30, "Brisk Walking", "Content", "Roti with mixed dal, Green salad"),
        (2800, 7.7, 35, "Morning Walk", "Positive", "Steamed idlis, Sambar, Coconut water")
    ]

    for i, (water, sleep, ex_min, ex_type, mood, meals) in enumerate(wellness_sample):
        past_date = today - timedelta(days=13 - i)
        log_wellness(
            user_id=user_id,
            log_date=past_date,
            water_ml=water,
            sleep_hours=sleep,
            exercise_mins=ex_min,
            exercise_type=ex_type,
            mood=mood,
            meal_notes=meals,
            notes="Demo recorded entry"
        )

    # 4. 8 Historical Vitals Records
    vitals_sample = [
        (118, 76, 70, 98.4, 73.0, 92.0, "Fasting", "Normal morning check", "Normal", "Within normal range"),
        (122, 78, 72, 98.6, 72.8, 126.0, "Postprandial", "After lunch check", "Normal", "Within normal range"),
        (119, 75, 68, 98.2, 72.6, 88.0, "Fasting", "Resting morning check", "Normal", "Within normal range"),
        (134, 86, 78, 98.5, 72.7, 95.0, "Fasting", "Mild work stress noted", "Warning", "Systolic BP slightly elevated (134 mmHg)"),
        (120, 78, 72, 98.4, 72.5, 118.0, "Postprandial", "Post dinner reading", "Normal", "Within normal range"),
        (117, 74, 69, 98.3, 72.4, 91.0, "Fasting", "Good recovery after weekend", "Normal", "Within normal range"),
        (121, 77, 71, 98.6, 72.5, 122.0, "Postprandial", "Regular weekly check", "Normal", "Within normal range"),
        (118, 76, 68, 98.4, 72.5, 89.0, "Fasting", "Optimal morning baseline", "Normal", "Within normal range")
    ]

    for i, (sys, dia, hr, temp, wt, gluc, ctx, notes, flag, flag_desc) in enumerate(vitals_sample):
        rec_time = datetime.now() - timedelta(days=14 - (i * 2), hours=i)
        log_vital(
            user_id=user_id,
            systolic_bp=sys,
            diastolic_bp=dia,
            heart_rate=hr,
            temperature_f=temp,
            weight_kg=wt,
            blood_glucose_mg_dl=gluc,
            glucose_context=ctx,
            notes=notes,
            flag_status=flag,
            flag_reasons=flag_desc,
            recorded_at=rec_time
        )

    # 5. Medicine Reminders
    m1 = add_medicine_reminder(
        user_id=user_id,
        medicine_name="Multivitamin Daily",
        dosage="1 Tablet",
        schedule_timing="Morning",
        time_str="08:30",
        instructions="Take after breakfast with water",
        start_date=today - timedelta(days=10),
        end_date=today + timedelta(days=50)
    )
    m2 = add_medicine_reminder(
        user_id=user_id,
        medicine_name="Omega-3 Fish Oil",
        dosage="1 Capsule",
        schedule_timing="Afternoon",
        time_str="13:30",
        instructions="Take after lunch",
        start_date=today - timedelta(days=10),
        end_date=today + timedelta(days=50)
    )
    m3 = add_medicine_reminder(
        user_id=user_id,
        medicine_name="Lubricating Eye Drops",
        dosage="1 Drop each eye",
        schedule_timing="Night",
        time_str="22:00",
        instructions="Use before sleep for screen fatigue",
        start_date=today - timedelta(days=5),
        end_date=today + timedelta(days=25)
    )
    # Mark morning med as taken today
    mark_medicine_taken(m1, user_id, today)

    # 6. Appointments
    add_appointment(
        user_id=user_id,
        doctor_name="Dr. Ananya Sharma",
        clinic_hospital="Apollo Health City",
        specialty="General Physician",
        appointment_date=today + timedelta(days=4),
        appointment_time="10:30 AM",
        notes="Annual wellness preventive review & blood panel check"
    )
    add_appointment(
        user_id=user_id,
        doctor_name="Dr. K. Srinivas",
        clinic_hospital="Care Dental Hospital",
        specialty="Dentist",
        appointment_date=today + timedelta(days=12),
        appointment_time="05:00 PM",
        notes="Routine 6-month dental cleaning and polish"
    )

    # 7. Sample Initial Chat
    save_chat_message(user_id, "user", "What is an ideal resting heart rate for healthy adults?")
    save_chat_message(
        user_id,
        "assistant",
        "A normal resting heart rate for healthy adults typically ranges from **60 to 100 beats per minute (BPM)**.\n\n"
        "• **Athletic individuals**: Well-conditioned athletes often have resting rates between 40–60 BPM because their heart muscle works more efficiently.\n"
        "• **Factors that influence heart rate**: Hydration, caffeine, stress, lack of sleep, and recent physical exertion.\n\n"
        "*(Note: This is educational guidance. If your resting heart rate is consistently above 100 or below 50 accompanied by dizziness, consult a physician.)*"
    )

    # 8. Sample Uploaded Medical Document
    user_dir = get_user_upload_dir(user_id)
    demo_file_name = "cbc_lipid_panel_apollo_diagnostics.txt"
    demo_file_path = os.path.join(user_dir, demo_file_name)
    if not os.path.exists(demo_file_path):
        with open(demo_file_path, "w", encoding="utf-8") as f:
            f.write(
                "============================================================\n"
                "APOLLO DIAGNOSTICS & PATHOLOGY LABORATORY\n"
                "CLINICAL BIOCHEMISTRY & HEMATOLOGY INVESTIGATION REPORT\n"
                "============================================================\n\n"
                "PATIENT DEMOGRAPHICS:\n"
                "Patient Name: Demo User        Age: 34 Years        Gender: Male\n"
                "Ref Doctor: Dr. Ananya Sharma  Date Collected: 2026-09-28\n"
                "Report Status: Verified & Approved by Pathologist\n\n"
                "------------------------------------------------------------\n"
                "COMPLETE BLOOD COUNT (CBC):\n"
                "------------------------------------------------------------\n"
                "• Hemoglobin:        14.8 g/dL          (Reference: 13.8 - 17.2 g/dL)  [NORMAL]\n"
                "• Total RBC Count:   5.10 mil/uL        (Reference: 4.50 - 5.90)       [NORMAL]\n"
                "• Total WBC Count:   6,800 /uL          (Reference: 4,000 - 11,000)    [NORMAL]\n"
                "• Neutrophils:       58 %               (Reference: 40 - 70 %)\n"
                "• Lymphocytes:       32 %               (Reference: 20 - 45 %)\n"
                "• Platelet Count:    240,000 /uL        (Reference: 150,000 - 450,000) [NORMAL]\n\n"
                "------------------------------------------------------------\n"
                "FASTING LIPID PROFILE:\n"
                "------------------------------------------------------------\n"
                "• Total Cholesterol: 182 mg/dL          (Desirable: < 200 mg/dL)       [DESIRABLE]\n"
                "• HDL (Good):        54 mg/dL           (Normal: > 40 mg/dL)           [OPTIMAL]\n"
                "• LDL (Bad):         102 mg/dL          (Optimal: < 100 mg/dL)         [NEAR OPTIMAL]\n"
                "• Triglycerides:     128 mg/dL          (Normal: < 150 mg/dL)          [NORMAL]\n\n"
                "------------------------------------------------------------\n"
                "CLINICAL INTERPRETATION:\n"
                "Hematological and lipid parameters demonstrate satisfactory cardiovascular\n"
                "metabolism. Continue balanced diet, adequate hydration, and routine physical activity.\n"
                "============================================================\n"
            )

    add_medical_document(
        user_id=user_id,
        title="Complete Blood Count (CBC) & Lipid Profile",
        category="Lab / Blood Test",
        report_date=today - timedelta(days=14),
        doctor_or_lab="Apollo Diagnostics",
        file_name=demo_file_name,
        file_path=demo_file_path,
        file_size_kb=round(os.path.getsize(demo_file_path) / 1024.0, 1),
        file_type="TXT",
        notes="Annual preventive checkup panel. All lipid and blood cell parameters within healthy reference range."
    )
