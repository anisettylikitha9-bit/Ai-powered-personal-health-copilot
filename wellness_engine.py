"""
wellness_engine.py - Clinical Vitals Validator, Health Habit Score Calculator,
and Smart Explainable Wellness Insights Engine.
Strictly adheres to safety rules: No disease diagnosis, fully transparent scoring.
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import database
from translations import t


# ==============================================================================
# 1. VITALS VALIDATOR & ANOMALY DETECTOR
# ==============================================================================

def validate_vitals(
    systolic_bp: Optional[int] = None,
    diastolic_bp: Optional[int] = None,
    heart_rate: Optional[int] = None,
    temperature_f: Optional[float] = None,
    weight_kg: Optional[float] = None,
    blood_glucose: Optional[float] = None,
    glucose_context: Optional[str] = "Fasting"
) -> Dict[str, Any]:
    """
    Validates vital readings against standard clinical reference guidelines.
    Flags readings that deviate from typical physiological ranges.
    Disclaimer: Strictly for user rechecking and physician discussion, never diagnosis.
    """
    flags = []
    status = "Normal"  # Normal, Warning, Urgent

    # Blood Pressure Validation (AHA / Indian guidelines)
    if systolic_bp is not None or diastolic_bp is not None:
        sys = systolic_bp or 120
        dia = diastolic_bp or 80

        if sys >= 180 or dia >= 120:
            status = "Urgent"
            flags.append(f"Systolic {sys} or Diastolic {dia} mmHg is in Hypertensive Crisis range (≥180 / ≥120). Recheck immediately; if accompanied by headache, chest discomfort or vision changes, seek emergency care.")
        elif sys >= 140 or dia >= 90:
            if status != "Urgent":
                status = "Warning"
            flags.append(f"Blood pressure {sys}/{dia} mmHg falls into Stage 2 Elevated range (≥140/90). Flagged for rechecking and physician review.")
        elif (130 <= sys <= 139) or (80 <= dia <= 89):
            if status != "Urgent":
                status = "Warning"
            flags.append(f"Blood pressure {sys}/{dia} mmHg falls into Stage 1 Elevated range (130-139 / 80-89). Consider monitoring lifestyle factors.")
        elif (120 <= sys <= 129) and dia < 80:
            flags.append(f"Systolic {sys} mmHg is slightly elevated (120-129 mmHg with normal diastolic).")
        elif sys < 90 or dia < 60:
            if status != "Urgent":
                status = "Warning"
            flags.append(f"Blood pressure {sys}/{dia} mmHg is low (<90/60 mmHg). If feeling dizzy or lightheaded, rest and hydrate.")

    # Heart Rate (Resting BPM)
    if heart_rate is not None:
        if heart_rate > 130 or heart_rate < 45:
            status = "Urgent"
            flags.append(f"Heart rate {heart_rate} BPM is significantly atypical (<45 or >130 BPM). Recheck at rest; consult a doctor if persistent.")
        elif heart_rate > 100:
            if status != "Urgent":
                status = "Warning"
            flags.append(f"Heart rate {heart_rate} BPM is elevated above normal resting rate (>100 BPM). Note recent caffeine, stress, or fever.")
        elif heart_rate < 55:
            if status != "Urgent":
                status = "Warning"
            flags.append(f"Heart rate {heart_rate} BPM is lower than average resting rate (<55 BPM). Normal in athletic individuals; recheck if symptomatic.")

    # Body Temperature (°F)
    if temperature_f is not None:
        if temperature_f >= 103.0:
            status = "Urgent"
            flags.append(f"Body temperature {temperature_f:.1f}°F is high fever (≥103.0°F). Seek professional medical evaluation promptly.")
        elif temperature_f > 100.4:
            if status != "Urgent":
                status = "Warning"
            flags.append(f"Body temperature {temperature_f:.1f}°F indicates fever (>100.4°F). Rest, hydrate, and monitor.")
        elif temperature_f > 99.0:
            flags.append(f"Body temperature {temperature_f:.1f}°F is slightly elevated low-grade temperature (99.1-100.4°F).")
        elif temperature_f < 95.0:
            status = "Urgent"
            flags.append(f"Body temperature {temperature_f:.1f}°F indicates hypothermia (<95.0°F). Warm up and seek medical attention.")

    # Blood Glucose (mg/dL)
    if blood_glucose is not None:
        ctx = (glucose_context or "Fasting").lower()
        if blood_glucose < 70.0:
            status = "Urgent"
            flags.append(f"Blood glucose {blood_glucose:.1f} mg/dL indicates hypoglycemia (<70 mg/dL). Consume fast-acting carbohydrates (juice/honey) and recheck in 15 mins.")
        elif "fasting" in ctx:
            if blood_glucose >= 126.0:
                if status != "Urgent":
                    status = "Warning"
                flags.append(f"Fasting blood glucose {blood_glucose:.1f} mg/dL is elevated (≥126 mg/dL). Flagged for rechecking and physician consultation.")
            elif blood_glucose >= 100.0:
                flags.append(f"Fasting blood glucose {blood_glucose:.1f} mg/dL is in the borderline range (100-125 mg/dL).")
        else:  # Postprandial / Random
            if blood_glucose >= 200.0:
                if status != "Urgent":
                    status = "Warning"
                flags.append(f"Post-meal blood glucose {blood_glucose:.1f} mg/dL is elevated (≥200 mg/dL). Flagged for physician review.")
            elif blood_glucose >= 140.0:
                flags.append(f"Post-meal blood glucose {blood_glucose:.1f} mg/dL is in the borderline range (140-199 mg/dL).")

    return {
        "status": status,
        "is_flagged": len(flags) > 0,
        "flags": flags,
        "flag_summary": "; ".join(flags) if flags else "All parameters within standard reference ranges.",
        "safety_disclaimer": "Flagged readings are highlighted for rechecking and professional advice only. This system never provides a clinical disease diagnosis."
    }


def calculate_bmi(weight_kg: Optional[float], height_cm: Optional[float]) -> Optional[Dict[str, Any]]:
    """Calculates BMI and returns classification based on WHO international thresholds."""
    if not weight_kg or not height_cm or height_cm <= 0 or weight_kg <= 0:
        return None

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    if bmi < 18.5:
        category = "Underweight"
        badge_class = "badge-warning"
    elif 18.5 <= bmi <= 24.9:
        category = "Healthy / Normal Weight"
        badge_class = "badge-normal"
    elif 25.0 <= bmi <= 29.9:
        category = "Overweight"
        badge_class = "badge-warning"
    else:
        category = "Obesity"
        badge_class = "badge-danger"

    return {
        "bmi": bmi,
        "category": category,
        "badge_class": badge_class,
        "height_cm": height_cm,
        "weight_kg": weight_kg
    }


# ==============================================================================
# 2. HEALTH HABIT SCORE (Transparent 0-100 Formula)
# ==============================================================================

def calculate_habit_score(user_id: int) -> Dict[str, Any]:
    """
    Calculates a transparent wellness score (0-100) across 5 lifestyle pillars (20 pts each):
    1. Hydration (Water vs Target)
    2. Sleep (Hours vs Target)
    3. Exercise (Minutes vs Target)
    4. Vitals Logging Consistency (Logged within past 3 days)
    5. Medication Adherence (Today's scheduled doses taken)
    Explicitly NOT a clinical medical diagnosis score.
    """
    today = date.today()
    goals = database.get_wellness_goals(user_id)
    today_wellness = database.get_wellness_for_date(user_id, today)
    
    # 1. Water Pillar (20 pts)
    target_water = goals.get("target_water_ml", 2500)
    actual_water = today_wellness["water_ml"] if today_wellness else 0
    water_ratio = min(actual_water / target_water, 1.0) if target_water > 0 else 0
    water_pts = round(water_ratio * 20.0, 1)

    # 2. Sleep Pillar (20 pts)
    target_sleep = goals.get("target_sleep_hours", 8.0)
    actual_sleep = today_wellness["sleep_hours"] if today_wellness else 0.0
    sleep_ratio = min(actual_sleep / target_sleep, 1.0) if target_sleep > 0 else 0
    sleep_pts = round(sleep_ratio * 20.0, 1)

    # 3. Exercise Pillar (20 pts)
    target_ex = goals.get("target_exercise_mins", 30)
    actual_ex = today_wellness["exercise_mins"] if today_wellness else 0
    ex_ratio = min(actual_ex / target_ex, 1.0) if target_ex > 0 else 0
    ex_pts = round(ex_ratio * 20.0, 1)

    # 4. Vitals Logging Pillar (20 pts)
    latest_vital = database.get_latest_vital(user_id)
    vitals_pts = 0.0
    vitals_msg = "No vitals logged yet"
    if latest_vital:
        rec_str = latest_vital["recorded_at"]
        try:
            rec_date = datetime.strptime(rec_str.split()[0], "%Y-%m-%d").date()
            diff_days = (today - rec_date).days
            if diff_days == 0:
                vitals_pts = 20.0
                vitals_msg = "Vitals logged today"
            elif diff_days <= 3:
                vitals_pts = 15.0
                vitals_msg = f"Vitals logged {diff_days} day(s) ago"
            elif diff_days <= 7:
                vitals_pts = 10.0
                vitals_msg = f"Vitals logged {diff_days} days ago"
            else:
                vitals_pts = 5.0
                vitals_msg = "Vitals logged over 7 days ago"
        except Exception:
            vitals_pts = 10.0
            vitals_msg = "Vitals on record"

    # 5. Medication Adherence Pillar (20 pts)
    reminders = database.get_medicine_reminders(user_id, active_only=True)
    if not reminders:
        med_pts = 20.0
        med_msg = "No scheduled medications (Full credit)"
    else:
        completed_ids = database.get_medicine_logs_for_date(user_id, today)
        med_ratio = len(completed_ids) / len(reminders)
        med_pts = round(min(med_ratio, 1.0) * 20.0, 1)
        med_msg = f"{len(completed_ids)} of {len(reminders)} medicines taken today"

    total_score = round(water_pts + sleep_pts + ex_pts + vitals_pts + med_pts)

    if total_score >= 85:
        score_grade = "Outstanding"
        grade_color = "#10b981"
    elif total_score >= 70:
        score_grade = "Great Consistency"
        grade_color = "#0284c7"
    elif total_score >= 50:
        score_grade = "Moderate Progress"
        grade_color = "#f59e0b"
    else:
        score_grade = "Focus on Habits"
        grade_color = "#f43f5e"

    return {
        "total_score": total_score,
        "score_grade": score_grade,
        "grade_color": grade_color,
        "pillars": {
            "water": {
                "name": "Hydration",
                "points": water_pts,
                "max": 20,
                "detail": f"{actual_water} / {target_water} ml ({round(water_ratio*100)}%)",
                "logic": "Calculated as (Actual Water / Target Water) × 20 points."
            },
            "sleep": {
                "name": "Sleep Duration",
                "points": sleep_pts,
                "max": 20,
                "detail": f"{actual_sleep:.1f} / {target_sleep:.1f} hrs ({round(sleep_ratio*100)}%)",
                "logic": "Calculated as (Logged Sleep / Target Sleep) × 20 points."
            },
            "exercise": {
                "name": "Physical Activity",
                "points": ex_pts,
                "max": 20,
                "detail": f"{actual_ex} / {target_ex} mins ({round(ex_ratio*100)}%)",
                "logic": "Calculated as (Logged Exercise / Target Exercise) × 20 points."
            },
            "vitals": {
                "name": "Vitals Monitoring",
                "points": vitals_pts,
                "max": 20,
                "detail": vitals_msg,
                "logic": "20 pts for today, 15 pts for 1-3 days, 10 pts for 4-7 days."
            },
            "medication": {
                "name": "Prescription Schedule",
                "points": med_pts,
                "max": 20,
                "detail": med_msg,
                "logic": "20 pts if all scheduled daily doses logged, or full credit if no meds active."
            }
        },
        "disclaimer": "This Habit Score is a lifestyle tracking heuristic based on your self-entered goals. It is NOT a clinical index or medical prognosis."
    }


# ==============================================================================
# 3. SMART EXPLAINABLE WELLNESS INSIGHTS
# ==============================================================================

def generate_smart_insights(user_id: int) -> List[Dict[str, str]]:
    """
    Compares recorded wellness and vitals data over time.
    Returns clear, explainable insights with explicit logic behind each insight.
    Strictly avoids clinical disease predictions.
    """
    insights = []
    wellness_logs = database.get_wellness_logs(user_id, days=14)
    vitals_logs = database.get_vitals(user_id, limit=10)
    goals = database.get_wellness_goals(user_id)

    # 1. Hydration Trend Insight
    if len(wellness_logs) >= 3:
        target_water = goals.get("target_water_ml", 2500)
        recent_water = [r["water_ml"] for r in wellness_logs[-7:]]
        avg_water = sum(recent_water) / len(recent_water) if recent_water else 0
        
        if avg_water >= target_water * 0.9:
            insights.append({
                "type": "positive",
                "icon": "💧",
                "category": "Hydration Consistency",
                "title": "Strong Hydration Habit Maintained",
                "description": f"Over the past week, your daily water intake averaged {round(avg_water)} ml, successfully meeting your {target_water} ml daily hydration target.",
                "rule_explained": f"Rule: Triggers positive when 7-day average water ({round(avg_water)} ml) is at or above 90% of user goal ({target_water} ml)."
            })
        else:
            insights.append({
                "type": "opportunity",
                "icon": "💧",
                "category": "Hydration Opportunity",
                "title": "Room to Increase Daily Hydration",
                "description": f"Your average water intake over the last week was {round(avg_water)} ml compared to your target of {target_water} ml.",
                "rule_explained": f"Rule: Triggers opportunity when 7-day average water ({round(avg_water)} ml) falls below 90% of target ({target_water} ml)."
            })

    # 2. Sleep Regularity Insight
    if len(wellness_logs) >= 3:
        target_sleep = goals.get("target_sleep_hours", 8.0)
        recent_sleep = [r["sleep_hours"] for r in wellness_logs[-7:]]
        avg_sleep = sum(recent_sleep) / len(recent_sleep) if recent_sleep else 0
        
        if avg_sleep >= target_sleep - 0.5:
            insights.append({
                "type": "positive",
                "icon": "🌙",
                "category": "Sleep Hygiene",
                "title": "Restful Sleep Pattern",
                "description": f"You are averaging {avg_sleep:.1f} hours of sleep per night, close to your ideal target of {target_sleep:.1f} hours.",
                "rule_explained": f"Rule: Triggers positive when 7-day average sleep ({avg_sleep:.1f} hrs) is within 0.5 hours of target ({target_sleep:.1f} hrs)."
            })
        else:
            insights.append({
                "type": "opportunity",
                "icon": "🌙",
                "category": "Sleep Opportunity",
                "title": "Sleep Duration Below Target",
                "description": f"You are averaging {avg_sleep:.1f} hours of nightly sleep, which is below your target of {target_sleep:.1f} hours. Consistent sleep supports immune function and mental focus.",
                "rule_explained": f"Rule: Triggers opportunity when average sleep is >0.5 hours below target."
            })

    # 3. Physical Activity Insight
    if len(wellness_logs) >= 3:
        recent_exercise = [r["exercise_mins"] for r in wellness_logs[-7:]]
        total_weekly_mins = sum(recent_exercise)
        
        if total_weekly_mins >= 150:
            insights.append({
                "type": "positive",
                "icon": "🏃",
                "category": "Physical Activity",
                "title": "Exceeded WHO Exercise Target",
                "description": f"You logged {total_weekly_mins} minutes of physical exercise this week, meeting the World Health Organization's guideline of 150+ minutes of moderate weekly activity.",
                "rule_explained": "Rule: Triggers positive when 7-day total exercise minutes ≥ 150 minutes (WHO recommended threshold)."
            })
        else:
            deficit = 150 - total_weekly_mins
            insights.append({
                "type": "opportunity",
                "icon": "🏃",
                "category": "Physical Activity",
                "title": "Activity Goal Progress",
                "description": f"You logged {total_weekly_mins} active minutes this week ({deficit} minutes away from the 150-minute weekly wellness benchmark). A brisk 20-minute daily walk can easily bridge this.",
                "rule_explained": "Rule: Triggers when 7-day exercise sum < 150 minutes."
            })

    # 4. Blood Pressure Stability Trend
    bp_readings = [r for r in vitals_logs if r["systolic_bp"] and r["diastolic_bp"]]
    if len(bp_readings) >= 2:
        recent_bp = bp_readings[:5]
        sys_vals = [r["systolic_bp"] for r in recent_bp]
        dia_vals = [r["diastolic_bp"] for r in recent_bp]
        avg_sys = sum(sys_vals) / len(sys_vals)
        avg_dia = sum(dia_vals) / len(dia_vals)
        max_sys_diff = max(sys_vals) - min(sys_vals)
        
        if max_sys_diff <= 15 and avg_sys < 130 and avg_dia < 85:
            insights.append({
                "type": "positive",
                "icon": "💓",
                "category": "Vitals Stability",
                "title": "Blood Pressure Readings Are Stable",
                "description": f"Your last {len(recent_bp)} blood pressure measurements show consistent stability (average {round(avg_sys)}/{round(avg_dia)} mmHg, variance ±{max_sys_diff} mmHg).",
                "rule_explained": f"Rule: Triggers when systolic variance ≤ 15 mmHg and averages remain below 130/85 mmHg across recent logs."
            })
        elif avg_sys >= 135 or avg_dia >= 88:
            insights.append({
                "type": "warning",
                "icon": "⚠️",
                "category": "Vitals Trend Review",
                "title": "Elevated Blood Pressure Readings Observed",
                "description": f"Your recent blood pressure checks average {round(avg_sys)}/{round(avg_dia)} mmHg. Consider sharing these self-recorded readings with your doctor for review.",
                "rule_explained": f"Rule: Triggers when multi-day average systolic ≥ 135 or diastolic ≥ 88 mmHg."
            })

    # Fallback if no logs yet
    if not insights:
        insights.append({
            "type": "info",
            "icon": "📊",
            "category": "Data Baseline",
            "title": "Building Your Personal Health Baseline",
            "description": "Log at least 3 days of vitals and wellness entries (or click 'Load Demo Health Data' in the sidebar) to unlock automatic trend comparisons and personalized habit insights.",
            "rule_explained": "Rule: Requires a minimum of 3 logged days to calculate statistical averages."
        })

    return insights
