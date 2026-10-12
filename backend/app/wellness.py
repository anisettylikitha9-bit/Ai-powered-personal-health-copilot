"""
backend/app/wellness.py - Wellness Tracker Operations & Habit Analytics
Provides CRUD operations for daily hydration, sleep, exercise, and mood logs,
plus habit score mathematical heuristics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import WellnessLog, WellnessGoal


def get_user_wellness_logs(db: Session, user_id: int, days: int = 30) -> List[WellnessLog]:
    """Retrieves chronologically recent wellness logs for a given user."""
    return (
        db.query(WellnessLog)
        .filter(WellnessLog.user_id == user_id)
        .order_by(desc(WellnessLog.log_date))
        .limit(days)
        .all()
    )


def create_wellness_log(
    db: Session,
    user_id: int,
    log_date: str,
    water_ml: int = 0,
    sleep_hours: float = 0.0,
    exercise_mins: int = 0,
    exercise_type: str = "",
    mood: str = "Neutral",
    meal_notes: str = "",
    notes: str = ""
) -> WellnessLog:
    """Creates or updates a wellness record for a specific date."""
    # Check if a log already exists for this date and user
    existing = (
        db.query(WellnessLog)
        .filter(WellnessLog.user_id == user_id, WellnessLog.log_date == log_date)
        .first()
    )
    if existing:
        existing.water_ml = water_ml
        existing.sleep_hours = sleep_hours
        existing.exercise_mins = exercise_mins
        existing.exercise_type = exercise_type
        existing.mood = mood
        existing.meal_notes = meal_notes
        existing.notes = notes
        db.commit()
        db.refresh(existing)
        return existing

    new_log = WellnessLog(
        user_id=user_id,
        log_date=log_date,
        water_ml=water_ml,
        sleep_hours=sleep_hours,
        exercise_mins=exercise_mins,
        exercise_type=exercise_type,
        mood=mood,
        meal_notes=meal_notes,
        notes=notes
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


def update_wellness_log(
    db: Session,
    record_id: int,
    user_id: int,
    water_ml: int,
    sleep_hours: float,
    exercise_mins: int,
    exercise_type: str,
    mood: str,
    meal_notes: str,
    notes: str
) -> Optional[WellnessLog]:
    """Updates an existing wellness record owned by the user."""
    log = (
        db.query(WellnessLog)
        .filter(WellnessLog.id == record_id, WellnessLog.user_id == user_id)
        .first()
    )
    if not log:
        return None

    log.water_ml = water_ml
    log.sleep_hours = sleep_hours
    log.exercise_mins = exercise_mins
    log.exercise_type = exercise_type
    log.mood = mood
    log.meal_notes = meal_notes
    log.notes = notes
    db.commit()
    db.refresh(log)
    return log


def delete_wellness_log(db: Session, record_id: int, user_id: int) -> bool:
    """Deletes a wellness record owned by the user."""
    log = (
        db.query(WellnessLog)
        .filter(WellnessLog.id == record_id, WellnessLog.user_id == user_id)
        .first()
    )
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True


def get_user_goals(db: Session, user_id: int) -> Optional[WellnessGoal]:
    """Retrieves user's health goals or initializes defaults."""
    goal = db.query(WellnessGoal).filter(WellnessGoal.user_id == user_id).first()
    if not goal:
        goal = WellnessGoal(user_id=user_id)
        db.add(goal)
        db.commit()
        db.refresh(goal)
    return goal


def calculate_habit_score(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Computes habit adherence score (0-100) based on actual saved entries from past 7 days.
    Heuristics:
    - Hydration adherence: up to 35 pts
    - Sleep restorative window: up to 35 pts
    - Physical exercise consistency: up to 30 pts
    """
    logs = (
        db.query(WellnessLog)
        .filter(WellnessLog.user_id == user_id)
        .order_by(desc(WellnessLog.log_date))
        .limit(7)
        .all()
    )
    goals = get_user_goals(db, user_id)

    if not logs:
        return {
            "habit_score": 0,
            "status_label": "No Data Recorded",
            "active_days_count": 0,
            "breakdown": {"hydration": 0, "sleep": 0, "exercise": 0}
        }

    water_pts = 0
    sleep_pts = 0
    exercise_pts = 0
    active_days = 0

    target_water = goals.target_water_ml if goals else 2500
    target_sleep = goals.target_sleep_hours if goals else 7.5
    target_ex = goals.target_exercise_mins if goals else 30

    for l in logs:
        # Water
        if l.water_ml >= target_water:
            water_pts += 35 / len(logs)
        elif l.water_ml > 0:
            water_pts += (35 / len(logs)) * (l.water_ml / target_water)

        # Sleep
        if 7.0 <= l.sleep_hours <= 9.0:
            sleep_pts += 35 / len(logs)
        elif l.sleep_hours > 0:
            sleep_pts += (35 / len(logs)) * min(1.0, l.sleep_hours / target_sleep)

        # Exercise
        if l.exercise_mins >= target_ex:
            exercise_pts += 30 / len(logs)
            active_days += 1
        elif l.exercise_mins > 0:
            exercise_pts += (30 / len(logs)) * (l.exercise_mins / target_ex)
            active_days += 1

    total = int(min(100, round(water_pts + sleep_pts + exercise_pts)))
    label = "Exceptional Habits" if total >= 80 else "Good Consistency" if total >= 50 else "Building Momentum"

    return {
        "habit_score": total,
        "status_label": label,
        "active_days_count": active_days,
        "breakdown": {
            "hydration": round(water_pts),
            "sleep": round(sleep_pts),
            "exercise": round(exercise_pts)
        }
    }
