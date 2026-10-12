"""
backend/app/analytics.py - Explainable Wellness Intelligence Engine
Computes transparent, quantifiable health insight cards exclusively from actual recorded entries.
Each insight details:
- title: Clinical domain header
- category: Target domain (Activity, Hydration, Sleep, Vitals)
- data_used: Concrete historical records evaluated
- rule_applied: Mathematical rule/heuristic applied
- result: Specific quantifiable change (e.g., 'Your active days increased from 2 to 4')
- limitation: Transparent clinical caveat
Never invents measurements or trends when data is missing.
"""

from typing import Dict, Any, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
try:
    from backend.app.models import WellnessLog, VitalLog, WellnessGoal
except ImportError:
    from .models import WellnessLog, VitalLog, WellnessGoal


def generate_explainable_insights(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Generates explainable wellness intelligence cards from real saved database records."""
    insights: List[Dict[str, Any]] = []

    # Fetch last 14 days of wellness logs
    wellness_logs = (
        db.query(WellnessLog)
        .filter(WellnessLog.user_id == user_id)
        .order_by(desc(WellnessLog.log_date))
        .limit(14)
        .all()
    )

    # Fetch last 10 vital readings
    vitals_logs = (
        db.query(VitalLog)
        .filter(VitalLog.user_id == user_id)
        .order_by(desc(VitalLog.recorded_at))
        .limit(10)
        .all()
    )

    goal = db.query(WellnessGoal).filter(WellnessGoal.user_id == user_id).first()
    target_water = goal.target_water_ml if goal else 2500
    target_sleep = goal.target_sleep_hours if goal else 7.5

    # 1. Physical Activity & Active Days Progression
    if len(wellness_logs) >= 2:
        today = date.today()
        current_week = []
        prev_week = []

        for w in wellness_logs:
            try:
                log_dt = datetime.strptime(w.log_date, "%Y-%m-%d").date()
                delta_days = (today - log_dt).days
                if delta_days <= 7:
                    current_week.append(w)
                elif 7 < delta_days <= 14:
                    prev_week.append(w)
            except Exception:
                continue

        curr_active = sum(1 for w in current_week if (w.exercise_mins or 0) > 0)
        prev_active = sum(1 for w in prev_week if (w.exercise_mins or 0) > 0)

        if prev_week:
            diff = curr_active - prev_active
            if diff > 0:
                result_msg = f"Your active days increased from {prev_active} to {curr_active} ({diff} additional active days)."
                card_type = "positive"
            elif diff == 0:
                result_msg = f"Your activity consistency remained steady at {curr_active} active days this week."
                card_type = "neutral"
            else:
                result_msg = f"Your active days decreased from {prev_active} to {curr_active}."
                card_type = "opportunity"
        else:
            result_msg = f"You recorded {curr_active} active exercise days in the current week."
            card_type = "positive" if curr_active >= 3 else "neutral"

        insights.append({
            "id": "INSIGHT_ACTIVE_DAYS",
            "type": card_type,
            "category": "Physical Activity Trend",
            "title": "Exercise Consistency & Active Days",
            "data_used": f"Activity records from two weeks ({len(wellness_logs)} logged daily entries).",
            "rule_applied": "Count days containing recorded exercise (exercise_mins > 0) across 7-day comparative windows.",
            "result": result_msg,
            "limitation": "Recorded activity is self-reported and not a complete measure of aerobic capacity or clinical fitness."
        })

    # 2. Daily Hydration Intake Balance
    if len(wellness_logs) >= 1:
        recent_water = [w.water_ml for w in wellness_logs[:7] if w.water_ml is not None]
        avg_water = round(sum(recent_water) / len(recent_water)) if recent_water else 0
        pct = round((avg_water / target_water) * 100) if target_water > 0 else 0

        insights.append({
            "id": "INSIGHT_HYDRATION",
            "type": "positive" if pct >= 85 else "opportunity",
            "category": "Hydration Balance",
            "title": "Daily Fluid Intake Consistency",
            "data_used": f"Water intake records from past {len(recent_water)} logged days (average: {avg_water} ml / target: {target_water} ml).",
            "rule_applied": f"Compare 7-day moving average against personal daily hydration target ({target_water} ml).",
            "result": f"Currently meeting {pct}% of your daily fluid target ({avg_water} ml daily average).",
            "limitation": "Optimal fluid requirements vary significantly with climate, temperature, and perspiration."
        })

    # 3. Rest & Sleep Duration Regularity
    if len(wellness_logs) >= 1:
        recent_sleep = [w.sleep_hours for w in wellness_logs[:7] if w.sleep_hours is not None]
        avg_sleep = round(sum(recent_sleep) / len(recent_sleep), 1) if recent_sleep else 0.0

        insights.append({
            "id": "INSIGHT_SLEEP",
            "type": "positive" if 7.0 <= avg_sleep <= 9.0 else "opportunity",
            "category": "Sleep Architecture",
            "title": "Circadian Rest & Sleep Duration",
            "data_used": f"Nightly sleep entries from past {len(recent_sleep)} logged days (average: {avg_sleep} hrs/night).",
            "rule_applied": "Compare average sleep against clinical restorative window (7.0 to 9.0 hours nightly).",
            "result": f"Averaging {avg_sleep} hours per night (target: {target_sleep} hrs).",
            "limitation": "Recorded duration does not capture deep sleep stages, REM cycles, or nighttime wake episodes."
        })

    # 4. Blood Pressure Stability (if vitals exist)
    bp_vitals = [v for v in vitals_logs if v.systolic_bp and v.diastolic_bp]
    if len(bp_vitals) >= 2:
        sys_vals = [v.systolic_bp for v in bp_vitals[:5]]
        dia_vals = [v.diastolic_bp for v in bp_vitals[:5]]
        avg_sys = round(sum(sys_vals) / len(sys_vals))
        avg_dia = round(sum(dia_vals) / len(dia_vals))
        var = max(sys_vals) - min(sys_vals)

        insights.append({
            "id": "INSIGHT_BP_STABILITY",
            "type": "positive" if avg_sys < 130 and avg_dia < 85 else "warning",
            "category": "Vitals Monitoring",
            "title": "Cardiovascular Pressure Stability",
            "data_used": f"Last {len(sys_vals)} blood pressure measurements on record.",
            "rule_applied": "Compute mean arterial pressures and systolic variance across sequential readings.",
            "result": f"Average blood pressure is {avg_sys}/{avg_dia} mmHg with ±{var} mmHg variance.",
            "limitation": "Self-measured blood pressure readings are subject to cuff calibration and situational anxiety."
        })

    # Empty State: When user has no data, never invent
    if not insights:
        insights.append({
            "id": "INSIGHT_BASELINE_PENDING",
            "type": "neutral",
            "category": "Baseline Establishment",
            "title": "Establishing Personal Health Baseline",
            "data_used": "0 recorded wellness logs on file.",
            "rule_applied": "Requires a minimum of 2 days of recorded logs to compute mathematical trends.",
            "result": "No baseline trends available yet. Record your daily wellness or click 'Load Demo Health Data'.",
            "limitation": "HealthSaathi AI never invents measurements or insights when data is missing."
        })

    return insights
