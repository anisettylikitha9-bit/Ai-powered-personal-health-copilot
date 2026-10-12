"""
pages/8_Wellness_Tracker.py - Daily Wellness Tracker & Lifestyle Habit Engine
Tracks hydration, sleep, exercise, and diet. Manages personal goals,
provides weekly summaries, habit score breakdowns, and transparent smart insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import database
import auth
from wellness_engine import calculate_habit_score, generate_smart_insights
from translations import t

st.set_page_config(page_title="Daily Wellness Tracker", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")
today = date.today()

# Header
st.markdown(f"""
<div class="health-header">
    <h2>🌱 {t('well_title', lang)}</h2>
    <p>{t('well_subtitle', lang)}</p>
</div>
""", unsafe_allow_html=True)

# Goals and Targets Expander
goals = database.get_wellness_goals(user_id)
with st.expander(f"🎯 {t('well_goals_header', lang)} (Customize Your Benchmarks)", expanded=False):
    with st.form("wellness_goals_form"):
        cg1, cg2, cg3, cg4 = st.columns(4)
        with cg1:
            g_water = st.number_input(t("well_target_water", lang), min_value=500, max_value=6000, value=int(goals["target_water_ml"]), step=250)
        with cg2:
            g_sleep = st.number_input(t("well_target_sleep", lang), min_value=4.0, max_value=14.0, value=float(goals["target_sleep_hours"]), step=0.5)
        with cg3:
            g_ex = st.number_input(t("well_target_exercise", lang), min_value=5, max_value=180, value=int(goals["target_exercise_mins"]), step=5)
        with cg4:
            g_steps = st.number_input("Daily Steps Goal", min_value=1000, max_value=30000, value=int(goals.get("target_steps", 8000)), step=500)

        if st.form_submit_button(t("well_save_goals", lang), type="primary"):
            database.save_wellness_goals(user_id, int(g_water), float(g_sleep), int(g_ex), int(g_steps))
            st.success("Personal wellness goals updated!")
            st.rerun()

# Date selector for logging (defaults to today)
c_dt, _ = st.columns([1, 2])
with c_dt:
    selected_date = st.date_input("Select Date to View / Log:", value=today, max_value=today)

existing_log = database.get_wellness_for_date(user_id, selected_date)

col_log, col_analytics = st.columns([1.1, 1.4])

with col_log:
    with st.container(border=True):
        st.markdown(f"#### 📝 {t('well_log_header', lang)} ({selected_date.strftime('%d %B %Y')})")

    # Quick Water Addition Buttons
    st.markdown("**Quick Water Add:**")
    qw1, qw2, qw3 = st.columns(3)
    curr_water = existing_log["water_ml"] if existing_log else 0

    with qw1:
        if st.button("💧 +250 ml (Cup)", use_container_width=True):
            database.log_wellness(
                user_id=user_id,
                log_date=selected_date,
                water_ml=curr_water + 250,
                sleep_hours=existing_log["sleep_hours"] if existing_log else 7.5,
                exercise_mins=existing_log["exercise_mins"] if existing_log else 30,
                exercise_type=existing_log["exercise_type"] if existing_log else "Walking",
                mood=existing_log["mood"] if existing_log else "Energetic",
                meal_notes=existing_log["meal_notes"] if existing_log else ""
            )
            st.rerun()
    with qw2:
        if st.button("🚰 +500 ml (Bottle)", use_container_width=True):
            database.log_wellness(
                user_id=user_id,
                log_date=selected_date,
                water_ml=curr_water + 500,
                sleep_hours=existing_log["sleep_hours"] if existing_log else 7.5,
                exercise_mins=existing_log["exercise_mins"] if existing_log else 30,
                exercise_type=existing_log["exercise_type"] if existing_log else "Walking",
                mood=existing_log["mood"] if existing_log else "Energetic",
                meal_notes=existing_log["meal_notes"] if existing_log else ""
            )
            st.rerun()
    with qw3:
        if st.button("🧴 +1000 ml", use_container_width=True):
            database.log_wellness(
                user_id=user_id,
                log_date=selected_date,
                water_ml=curr_water + 1000,
                sleep_hours=existing_log["sleep_hours"] if existing_log else 7.5,
                exercise_mins=existing_log["exercise_mins"] if existing_log else 30,
                exercise_type=existing_log["exercise_type"] if existing_log else "Walking",
                mood=existing_log["mood"] if existing_log else "Energetic",
                meal_notes=existing_log["meal_notes"] if existing_log else ""
            )
            st.rerun()

    st.markdown("---")

    with st.form("wellness_log_form"):
        f_water = st.number_input(
            t("well_water_total", lang),
            min_value=0,
            max_value=10000,
            value=int(existing_log["water_ml"]) if existing_log else 2000,
            step=100
        )
        
        c_sl, c_ex = st.columns(2)
        with c_sl:
            f_sleep = st.number_input(
                t("well_sleep", lang),
                min_value=0.0,
                max_value=24.0,
                value=float(existing_log["sleep_hours"]) if existing_log else 7.5,
                step=0.5
            )
        with c_ex:
            f_ex_min = st.number_input(
                t("well_exercise_min", lang),
                min_value=0,
                max_value=360,
                value=int(existing_log["exercise_mins"]) if existing_log else 30,
                step=5
            )

        c_extype, c_mood = st.columns(2)
        with c_extype:
            ex_types = ["Brisk Walking", "Yoga & Meditation", "Jogging / Running", "Cycling", "Strength Training", "Swimming", "Stretching", "Other / None"]
            curr_type = existing_log["exercise_type"] if existing_log and existing_log["exercise_type"] in ex_types else "Brisk Walking"
            f_ex_type = st.selectbox(t("well_exercise_type", lang), ex_types, index=ex_types.index(curr_type))
        with c_mood:
            mood_options = ["Energetic", "Calm & Focused", "Good", "Normal", "Tired", "Stressed"]
            curr_mood = existing_log["mood"] if existing_log and existing_log["mood"] in mood_options else "Energetic"
            f_mood = st.selectbox(t("well_mood", lang), mood_options, index=mood_options.index(curr_mood))

        f_meals = st.text_area(
            t("well_meals", lang),
            value=existing_log["meal_notes"] if existing_log and existing_log["meal_notes"] else "",
            placeholder="e.g. Oatmeal with fruit, lentils, spinach curry, whole wheat rotis, low sodium"
        )
        
        f_notes = st.text_input("General Reflections", value=existing_log["notes"] if existing_log and existing_log["notes"] else "")

        btn_save = st.form_submit_button(t("well_save_btn", lang), type="primary", use_container_width=True)

        if btn_save:
            database.log_wellness(
                user_id=user_id,
                log_date=selected_date,
                water_ml=int(f_water),
                sleep_hours=float(f_sleep),
                exercise_mins=int(f_ex_min),
                exercise_type=f_ex_type,
                mood=f_mood,
                meal_notes=f_meals,
                notes=f_notes
            )
            st.success("Daily wellness record saved successfully!")
            st.rerun()

with col_analytics:
    # Transparent Health Habit Score Display
    habit_data = calculate_habit_score(user_id)
    
    with st.container(border=True):
        st.markdown(f"#### 🏆 Health Habit Score Breakdown ({habit_data['total_score']} / 100)")
        st.markdown(f"<p style='font-size:0.82rem; color:#64748b;'>{habit_data['disclaimer']}</p>", unsafe_allow_html=True)

        for k, p in habit_data["pillars"].items():
            pillar_html = (
                f'<div style="margin-bottom: 0.65rem;">'
                f'<div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 600;">'
                f'<span>{p["name"]}</span>'
                f'<span style="color: #0284c7;">{p["points"]} / {p["max"]} pts</span>'
                f'</div>'
                f'<div style="font-size: 0.78rem; color: #64748b;">{p["detail"]}</div>'
                f'</div>'
            )
            st.markdown(pillar_html, unsafe_allow_html=True)
            st.progress(p["points"] / p["max"])

# Weekly Interactive Trends & Statistical Summary
st.markdown("---")
st.markdown("### 📊 14-Day Lifestyle Trends & Visual Progress")

logs_14d = database.get_wellness_logs(user_id, days=14)

if logs_14d:
    df_logs = pd.DataFrame([dict(r) for r in logs_14d])
    df_logs["log_date"] = pd.to_datetime(df_logs["log_date"])

    # 3 Summary Stat Metrics
    avg_water = df_logs["water_ml"].mean()
    avg_sleep = df_logs["sleep_hours"].mean()
    sum_ex = df_logs["exercise_mins"].sum()

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-title">14-Day Avg Water</div>'
            f'<div class="metric-value">{round(avg_water)} <span style="font-size:0.9rem; font-weight:normal;">ml/day</span></div>'
            f'<div class="metric-sub">Goal: {goals["target_water_ml"]} ml</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f'<div class="metric-box teal">'
            f'<div class="metric-title">14-Day Avg Sleep</div>'
            f'<div class="metric-value">{avg_sleep:.1f} <span style="font-size:0.9rem; font-weight:normal;">hrs/night</span></div>'
            f'<div class="metric-sub">Goal: {goals["target_sleep_hours"]} hrs</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f'<div class="metric-box emerald">'
            f'<div class="metric-title">Total Active Exercise</div>'
            f'<div class="metric-value">{sum_ex} <span style="font-size:0.9rem; font-weight:normal;">mins</span></div>'
            f'<div class="metric-sub">Across {len(df_logs)} logged days</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Plotly Charts
    c_ch_water, c_ch_sleep = st.columns(2)
    with c_ch_water:
        fig_w = px.bar(
            df_logs,
            x="log_date",
            y="water_ml",
            title="Daily Hydration Progression (ml)",
            color_discrete_sequence=["#0284c7"]
        )
        fig_w.add_hline(y=goals["target_water_ml"], line_dash="dash", line_color="#0d9488", annotation_text="Goal")
        fig_w.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="#ffffff")
        st.plotly_chart(fig_w, use_container_width=True)

    with c_ch_sleep:
        fig_s = px.bar(
            df_logs,
            x="log_date",
            y="exercise_mins",
            title="Exercise Duration by Day (Minutes)",
            color="exercise_type",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_s.add_hline(y=goals["target_exercise_mins"], line_dash="dash", line_color="#ef4444", annotation_text="Daily Goal")
        fig_s.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="#ffffff")
        st.plotly_chart(fig_s, use_container_width=True)

else:
    st.info("No wellness records found in the last 14 days. Start recording above or load demo health data.")

# Smart Wellness Insights Section
st.markdown("---")
st.markdown(f"### 💡 {t('ins_title', lang)}")
wellness_insights = generate_smart_insights(user_id)

for ins in wellness_insights:
    badge_type = ins.get("type", "info")
    badge_class = "badge-normal" if badge_type == "positive" else ("badge-warning" if badge_type == "opportunity" else "badge-info")
    card_ins_html = (
        f'<div class="health-card" style="border-left: 4px solid {"#10b981" if badge_type=="positive" else ("#f59e0b" if badge_type=="opportunity" else "#0284c7")};">'
        f'<div style="display: flex; justify-content: space-between; align-items: center;">'
        f'<div style="font-weight: 700; color: #0f172a;">{ins.get("icon", "💡")} {ins["title"]}</div>'
        f'<span class="{badge_class}">{ins.get("category", "Habit")}</span>'
        f'</div>'
        f'<p style="color: #475569; margin: 0.5rem 0; font-size: 0.92rem;">{ins["description"]}</p>'
        f'<div style="background: #f8fafc; border-radius: 6px; padding: 0.4rem 0.6rem; font-size: 0.78rem; color: #64748b;">'
        f'<strong>{t("ins_rule_label", lang)}</strong> {ins["rule_explained"]}'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_ins_html, unsafe_allow_html=True)

# Global Medical Disclaimer
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 2rem;">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)
