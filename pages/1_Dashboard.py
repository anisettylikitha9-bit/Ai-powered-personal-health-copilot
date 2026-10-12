"""
pages/1_Dashboard.py - Personal Health & Wellness Dashboard
Presents habit scores, today's snapshot, vitals cards, weekly interactive Plotly charts,
smart explainable wellness insights, and instant quick-action controls.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import database
import auth
from wellness_engine import calculate_habit_score, calculate_bmi, generate_smart_insights
from translations import t

st.set_page_config(page_title="Personal Health Dashboard", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")
today = date.today()

# Header
st.markdown(f"""
<div class="health-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h2>📊 {t('nav_dashboard', lang)}</h2>
            <p>{t('dash_welcome', lang)}, <strong>{st.session_state.full_name}</strong>! {t('dash_overview', lang)}</p>
        </div>
        <div style="font-size: 0.9rem; background: rgba(255,255,255,0.2); padding: 0.4rem 0.9rem; border-radius: 20px;">
            📅 {today.strftime("%A, %d %B %Y")}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 1. Top Highlights: Habit Score & Today's Snapshot
col_score, col_today = st.columns([1.1, 1.9])

habit_data = calculate_habit_score(user_id)
today_wellness = database.get_wellness_for_date(user_id, today)
goals = database.get_wellness_goals(user_id)

with col_score:
    with st.container(border=True):
        st.markdown(f"#### 🏆 {t('dash_habit_score', lang)}")
        
        # Plotly Gauge Chart for Score
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=habit_data["total_score"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': habit_data["score_grade"], 'font': {'size': 16, 'color': habit_data["grade_color"]}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                'bar': {'color': habit_data["grade_color"]},
                'bgcolor': "white",
                'borderwidth': 1,
                'bordercolor': "#e2e8f0",
                'steps': [
                    {'range': [0, 50], 'color': '#fee2e2'},
                    {'range': [50, 75], 'color': '#fef3c7'},
                    {'range': [75, 100], 'color': '#ecfdf5'}
                ]
            }
        ))
        fig_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=20, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

        with st.expander("ℹ️ How this score is calculated (Transparent Breakdown)"):
            st.markdown(f"<p style='font-size:0.8rem; color:#64748b;'>{habit_data['disclaimer']}</p>", unsafe_allow_html=True)
            for k, p in habit_data["pillars"].items():
                st.markdown(f"• **{p['name']}**: `{p['points']} / {p['max']} pts` — *{p['detail']}*<br><span style='font-size:0.75rem; color:#64748b;'>{p['logic']}</span>", unsafe_allow_html=True)

with col_today:
    with st.container(border=True):
        st.markdown(f"#### 🎯 {t('dash_today_summary', lang)}")
        
        w_water = today_wellness["water_ml"] if today_wellness else 0
        t_water = goals.get("target_water_ml", 2500)
        w_sleep = today_wellness["sleep_hours"] if today_wellness else 0.0
        t_sleep = goals.get("target_sleep_hours", 8.0)
        w_ex = today_wellness["exercise_mins"] if today_wellness else 0
        t_ex = goals.get("target_exercise_mins", 30)

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(
                f'<div class="metric-box">'
                f'<div class="metric-title">{t("dash_water", lang)}</div>'
                f'<div class="metric-value">{w_water} <span style="font-size:0.9rem; font-weight:normal;">ml</span></div>'
                f'<div class="metric-sub">Goal: {t_water} ml</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.progress(min(w_water / t_water, 1.0) if t_water > 0 else 0)

        with mc2:
            st.markdown(
                f'<div class="metric-box teal">'
                f'<div class="metric-title">{t("dash_sleep", lang)}</div>'
                f'<div class="metric-value">{w_sleep:.1f} <span style="font-size:0.9rem; font-weight:normal;">hrs</span></div>'
                f'<div class="metric-sub">Goal: {t_sleep:.1f} hrs</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.progress(min(w_sleep / t_sleep, 1.0) if t_sleep > 0 else 0)

        with mc3:
            st.markdown(
                f'<div class="metric-box emerald">'
                f'<div class="metric-title">{t("dash_exercise", lang)}</div>'
                f'<div class="metric-value">{w_ex} <span style="font-size:0.9rem; font-weight:normal;">min</span></div>'
                f'<div class="metric-sub">Goal: {t_ex} min</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.progress(min(w_ex / t_ex, 1.0) if t_ex > 0 else 0)

        # Quick Add Water Button right on card
        q_col1, q_col2 = st.columns([1, 1])
        with q_col1:
            if st.button("💧 +250 ml Water", use_container_width=True):
                new_water = w_water + 250
                database.log_wellness(
                    user_id=user_id,
                    log_date=today,
                    water_ml=new_water,
                    sleep_hours=w_sleep,
                    exercise_mins=w_ex,
                    exercise_type=today_wellness["exercise_type"] if today_wellness else None,
                    mood=today_wellness["mood"] if today_wellness else None,
                    meal_notes=today_wellness["meal_notes"] if today_wellness else None
                )
                st.rerun()
        with q_col2:
            st.page_link("pages/8_Wellness_Tracker.py", label=f"✏️ {t('dash_log_wellness', lang)}", use_container_width=True)

st.markdown("---")

# 2. Latest Vitals Section
st.markdown(f"### 💓 {t('dash_vitals_summary', lang)}")
latest_v = database.get_latest_vital(user_id)
profile = database.get_profile(user_id)
bmi_res = calculate_bmi(profile["weight_kg"] if profile else None, profile["height_cm"] if profile else None)

vcol1, vcol2, vcol3, vcol4, vcol5 = st.columns(5)
with vcol1:
    bp_val = f"{latest_v['systolic_bp']}/{latest_v['diastolic_bp']}" if latest_v and latest_v['systolic_bp'] and latest_v['diastolic_bp'] else "—"
    bp_sub = latest_v["flag_status"] if latest_v else "No logs"
    st.markdown(
        f'<div class="metric-box">'
        f'<div class="metric-title">{t("dash_bp", lang)}</div>'
        f'<div class="metric-value">{bp_val}</div>'
        f'<div class="metric-sub">mmHg • {bp_sub}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with vcol2:
    hr_val = f"{latest_v['heart_rate']}" if latest_v and latest_v['heart_rate'] else "—"
    st.markdown(
        f'<div class="metric-box rose">'
        f'<div class="metric-title">{t("dash_heart_rate", lang)}</div>'
        f'<div class="metric-value">{hr_val}</div>'
        f'<div class="metric-sub">BPM (Resting)</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with vcol3:
    temp_val = f"{latest_v['temperature_f']:.1f}°F" if latest_v and latest_v['temperature_f'] else "—"
    st.markdown(
        f'<div class="metric-box amber">'
        f'<div class="metric-title">{t("dash_temp", lang)}</div>'
        f'<div class="metric-value">{temp_val}</div>'
        f'<div class="metric-sub">Oral Body Temp</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with vcol4:
    gluc_val = f"{latest_v['blood_glucose_mg_dl']:.0f}" if latest_v and latest_v['blood_glucose_mg_dl'] else "—"
    gluc_ctx = latest_v["glucose_context"] if latest_v and latest_v["glucose_context"] else "mg/dL"
    st.markdown(
        f'<div class="metric-box teal">'
        f'<div class="metric-title">{t("dash_glucose", lang)}</div>'
        f'<div class="metric-value">{gluc_val}</div>'
        f'<div class="metric-sub">{gluc_ctx}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with vcol5:
    bmi_val = f"{bmi_res['bmi']}" if bmi_res else "—"
    bmi_cat = bmi_res["category"] if bmi_res else "Set height & wt"
    st.markdown(
        f'<div class="metric-box emerald">'
        f'<div class="metric-title">{t("dash_bmi", lang)}</div>'
        f'<div class="metric-value">{bmi_val}</div>'
        f'<div class="metric-sub">{bmi_cat}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# 3. Interactive Weekly Charts
st.markdown(f"### 📈 {t('dash_recent_trend', lang)}")

wellness_logs = database.get_wellness_logs(user_id, days=14)
vitals_history = database.get_vitals(user_id, limit=14)

tab_well_chart, tab_bp_chart = st.tabs(["🌱 Daily Wellness (Hydration & Sleep)", "💓 Cardiovascular Vitals (BP & Heart Rate)"])

with tab_well_chart:
    if wellness_logs:
        df_w = pd.DataFrame([dict(r) for r in wellness_logs])
        df_w["log_date"] = pd.to_datetime(df_w["log_date"])
        
        c_ch1, c_ch2 = st.columns(2)
        with c_ch1:
            fig_water = px.bar(
                df_w,
                x="log_date",
                y="water_ml",
                title="Water Intake Trend (ml)",
                labels={"water_ml": "Water (ml)", "log_date": "Date"},
                color_discrete_sequence=["#0284c7"]
            )
            fig_water.add_hline(y=t_water, line_dash="dash", line_color="#0d9488", annotation_text="Goal")
            fig_water.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="#ffffff")
            st.plotly_chart(fig_water, use_container_width=True)

        with c_ch2:
            fig_sleep = px.line(
                df_w,
                x="log_date",
                y="sleep_hours",
                title="Sleep Duration (Hours)",
                markers=True,
                labels={"sleep_hours": "Sleep (Hours)", "log_date": "Date"},
                color_discrete_sequence=["#0d9488"]
            )
            fig_sleep.add_hline(y=t_sleep, line_dash="dash", line_color="#f59e0b", annotation_text="Target")
            fig_sleep.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="#ffffff")
            st.plotly_chart(fig_sleep, use_container_width=True)
    else:
        st.info("No wellness logs available to chart yet. Click 'Load Demo Health Data' in the sidebar or log daily wellness.")

with tab_bp_chart:
    if vitals_history:
        v_list = [dict(r) for r in reversed(vitals_history)]
        df_v = pd.DataFrame(v_list)
        df_v["recorded_at"] = pd.to_datetime(df_v["recorded_at"])
        
        fig_bp = go.Figure()
        if "systolic_bp" in df_v.columns and df_v["systolic_bp"].notnull().any():
            fig_bp.add_trace(go.Scatter(x=df_v["recorded_at"], y=df_v["systolic_bp"], mode='lines+markers', name='Systolic BP (mmHg)', line=dict(color='#0284c7', width=2)))
        if "diastolic_bp" in df_v.columns and df_v["diastolic_bp"].notnull().any():
            fig_bp.add_trace(go.Scatter(x=df_v["recorded_at"], y=df_v["diastolic_bp"], mode='lines+markers', name='Diastolic BP (mmHg)', line=dict(color='#0d9488', width=2)))
        if "heart_rate" in df_v.columns and df_v["heart_rate"].notnull().any():
            fig_bp.add_trace(go.Scatter(x=df_v["recorded_at"], y=df_v["heart_rate"], mode='lines+markers', name='Heart Rate (BPM)', line=dict(color='#f43f5e', dash='dot')))

        fig_bp.update_layout(
            title="Blood Pressure & Heart Rate Progression",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="#ffffff",
            xaxis_title="Date Recorded",
            yaxis_title="Measurement (mmHg / BPM)"
        )
        st.plotly_chart(fig_bp, use_container_width=True)
    else:
        st.info("No vitals recorded yet. Record measurements to visualize cardiovascular trends.")

# 4. Smart Explainable Wellness Insights
st.markdown("---")
st.markdown(f"### 💡 {t('ins_title', lang)}")
insights = generate_smart_insights(user_id)

for ins in insights:
    icon = ins.get("icon", "💡")
    badge_type = ins.get("type", "info")
    badge_class = "badge-normal" if badge_type == "positive" else ("badge-warning" if badge_type == "opportunity" else "badge-info")
    
    border_c = '#10b981' if badge_type=='positive' else ('#f59e0b' if badge_type=='opportunity' else '#0284c7')
    ins_html = (
        f'<div class="health-card" style="border-left: 4px solid {border_c};">'
        f'<div style="display: flex; justify-content: space-between; align-items: center;">'
        f'<div style="font-weight: 700; color: #0f172a; font-size: 1.05rem;">{icon} {ins["title"]}</div>'
        f'<span class="{badge_class}">{ins.get("category", "Insight")}</span>'
        f'</div>'
        f'<p style="color: #475569; margin: 0.5rem 0; font-size: 0.92rem;">{ins["description"]}</p>'
        f'<div style="background: #f8fafc; border-radius: 6px; padding: 0.4rem 0.6rem; font-size: 0.78rem; color: #64748b;">'
        f'<strong>{t("ins_rule_label", lang)}</strong> {ins["rule_explained"]}'
        f'</div>'
        f'</div>'
    )
    st.markdown(ins_html, unsafe_allow_html=True)

# 5. Bottom Split: Today's Medicines & Upcoming Appointments
st.markdown("---")
c_meds, c_apts = st.columns(2)

with c_meds:
    st.markdown(f"#### 💊 {t('dash_meds_due', lang)}")
    active_meds = database.get_medicine_reminders(user_id, active_only=True)
    completed_today = database.get_medicine_logs_for_date(user_id, today)

    if active_meds:
        for med in active_meds:
            med_id = med["id"]
            is_done = med_id in completed_today
            
            med_inst = f" • {med['instructions']}" if med['instructions'] else ""
            card_med_html = (
                f'<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">'
                f'<div>'
                f'<strong>{med["medicine_name"]}</strong> — <span style="color: #64748b;">{med["dosage"]}</span><br>'
                f'<span style="font-size: 0.8rem; color: #0d9488;">⏰ {med["time_str"]} ({med["schedule_timing"]})</span>'
                f'<span style="font-size: 0.78rem; color: #64748b;">{med_inst}</span>'
                f'</div>'
                f'</div>'
            )
            st.markdown(card_med_html, unsafe_allow_html=True)
            
            # Interactive toggle button
            btn_label = f"✅ {'Mark as Pending' if is_done else 'Mark as Taken'}"
            if st.button(f"{btn_label} ({med['medicine_name']})", key=f"dash_med_{med_id}"):
                if is_done:
                    database.unmark_medicine_taken(med_id, user_id, today)
                else:
                    database.mark_medicine_taken(med_id, user_id, today)
                st.rerun()
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💊</div>
            <div class="empty-state-title">No Active Prescriptions</div>
            <div>Keep your scheduled medications organized.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/6_Medicine_Reminders.py", label=f"➕ {t('dash_add_med', lang)}")

with c_apts:
    st.markdown(f"#### 📅 {t('dash_appointments_due', lang)}")
    apts = database.get_appointments(user_id, status_filter="Scheduled")
    if apts:
        for apt in apts[:3]:
            apt_note = f"<div style='font-size: 0.78rem; color: #64748b; font-style: italic; margin-top: 0.2rem;'>Note: {apt['notes']}</div>" if apt['notes'] else ""
            apt_card_html = (
                f'<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;">'
                f'<div style="font-weight: 700; color: #0284c7;">{apt["doctor_name"]} ({apt["specialty"] or "Specialist"})</div>'
                f'<div style="font-size: 0.82rem; color: #475569;">📍 {apt["clinic_hospital"] or "Clinic/Hospital"}</div>'
                f'<div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">'
                f'📅 <strong>{apt["appointment_date"]}</strong> at <strong>{apt["appointment_time"]}</strong>'
                f'</div>'
                f'{apt_note}'
                f'</div>'
            )
            st.markdown(apt_card_html, unsafe_allow_html=True)
        st.page_link("pages/7_Appointments.py", label=f"👉 View All Appointments", use_container_width=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📅</div>
            <div class="empty-state-title">No Upcoming Appointments</div>
            <div>Record your next doctor visit or health checkup.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/7_Appointments.py", label=f"➕ {t('dash_book_apt', lang)}")

# Global Medical Disclaimer
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 2rem;">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)
