"""
pages/3_Vitals_Tracker.py - Vitals Tracker & Physiological Anomaly Flagging
Enables logging of BP, Heart Rate, Temperature, Glucose, and Weight.
Validates physiological ranges, flags readings for rechecking, and visualizes trends.
Strictly non-diagnostic.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import database
import auth
from wellness_engine import validate_vitals
from translations import t

st.set_page_config(page_title="Vitals Tracker", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")

# Header
st.markdown(f"""
<div class="health-header">
    <h2>💓 {t('vitals_title', lang)}</h2>
    <p>{t('vitals_subtitle', lang)}</p>
</div>
""", unsafe_allow_html=True)

# Main Two-Column Layout
col_log, col_visuals = st.columns([1.1, 1.9])

with col_log:
    with st.container(border=True):
        st.markdown(f"#### ➕ {t('vitals_log_header', lang)}")

    with st.form("log_vitals_form"):
        c1, c2 = st.columns(2)
        with c1:
            sys_bp = st.number_input(t("vitals_systolic", lang), min_value=60, max_value=260, value=120, step=1)
            hr = st.number_input(t("vitals_hr", lang), min_value=30, max_value=220, value=72, step=1)
            weight = st.number_input(t("vitals_weight_kg", lang), min_value=20.0, max_value=250.0, value=70.0, step=0.5)

        with c2:
            dia_bp = st.number_input(t("vitals_diastolic", lang), min_value=40, max_value=160, value=80, step=1)
            temp_f = st.number_input(t("vitals_temperature", lang), min_value=93.0, max_value=108.0, value=98.6, step=0.1)
            glucose = st.number_input(t("vitals_glucose", lang), min_value=40.0, max_value=500.0, value=95.0, step=1.0)

        glucose_type = st.selectbox(
            t("vitals_glucose_type", lang),
            ["Fasting (8+ hrs)", "Postprandial (2 hrs post-meal)", "Random Check"]
        )

        v_notes = st.text_input(t("vitals_notes", lang), placeholder="e.g. Taken before morning coffee")

        btn_submit = st.form_submit_button(t("vitals_save_btn", lang), type="primary", use_container_width=True)

        if btn_submit:
            # 1. Validation & Anomaly Tagging
            validation = validate_vitals(
                systolic_bp=int(sys_bp),
                diastolic_bp=int(dia_bp),
                heart_rate=int(hr),
                temperature_f=float(temp_f),
                weight_kg=float(weight),
                blood_glucose=float(glucose),
                glucose_context=glucose_type
            )

            # 2. Insert into SQLite
            database.log_vital(
                user_id=user_id,
                systolic_bp=int(sys_bp),
                diastolic_bp=int(dia_bp),
                heart_rate=int(hr),
                temperature_f=float(temp_f),
                weight_kg=float(weight),
                blood_glucose_mg_dl=float(glucose),
                glucose_context=glucose_type,
                notes=v_notes,
                flag_status=validation["status"],
                flag_reasons=validation["flag_summary"]
            )

            # 3. Notification feedback
            if validation["status"] == "Urgent":
                st.error(f"🚨 {validation['flag_summary']}\n\n{validation['safety_disclaimer']}")
            elif validation["status"] == "Warning":
                st.warning(f"⚠️ {validation['flag_summary']}\n\n{validation['safety_disclaimer']}")
            else:
                st.success(f"✅ {t('vitals_saved_success', lang)}")
            st.rerun()

    # Reference Thresholds Quick Card
    ref_guide_html = (
        '<div class="health-card" style="font-size: 0.82rem; color: #475569; margin-top: 1rem;">'
        '<h5 style="color: #0284c7; margin-top: 0;">📖 Reference Guidelines</h5>'
        '• <strong>Blood Pressure:</strong> Normal < 120/80 mmHg; Stage 2 ≥ 140/90 mmHg.<br>'
        '• <strong>Heart Rate:</strong> Resting 60–100 BPM.<br>'
        '• <strong>Body Temp:</strong> Normal 97.0–99.0°F; Fever > 100.4°F.<br>'
        '• <strong>Fasting Glucose:</strong> Normal 70–99 mg/dL; Pre-diabetes 100–125 mg/dL.<br>'
        '<div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.4rem;">'
        '*Source: AHA & WHO standard physiological ranges. For informational screening only.'
        '</div>'
        '</div>'
    )
    st.markdown(ref_guide_html, unsafe_allow_html=True)

with col_visuals:
    vitals_history = database.get_vitals(user_id, limit=30)

    if vitals_history:
        # Chart Tabs
        st.markdown(f"#### 📈 {t('vitals_charts_header', lang)}")
        
        tab_bp, tab_gluc, tab_temp = st.tabs(["💓 Blood Pressure & Pulse", "🩸 Blood Glucose", "🌡️ Temp & Weight"])

        v_list = [dict(r) for r in reversed(vitals_history)]
        df_v = pd.DataFrame(v_list)
        df_v["recorded_at"] = pd.to_datetime(df_v["recorded_at"])

        with tab_bp:
            fig_bp = go.Figure()
            fig_bp.add_trace(go.Scatter(x=df_v["recorded_at"], y=df_v["systolic_bp"], mode='lines+markers', name='Systolic BP (mmHg)', line=dict(color='#0284c7', width=2.5)))
            fig_bp.add_trace(go.Scatter(x=df_v["recorded_at"], y=df_v["diastolic_bp"], mode='lines+markers', name='Diastolic BP (mmHg)', line=dict(color='#0d9488', width=2.5)))
            fig_bp.add_trace(go.Scatter(x=df_v["recorded_at"], y=df_v["heart_rate"], mode='lines+markers', name='Heart Rate (BPM)', line=dict(color='#f43f5e', dash='dot')))
            
            # Clinical reference guide bands
            fig_bp.add_hline(y=140, line_dash="dash", line_color="#ef4444", annotation_text="Stage 2 BP (140)")
            fig_bp.add_hline(y=120, line_dash="dot", line_color="#10b981", annotation_text="Optimal BP (120)")
            
            fig_bp.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor="#ffffff")
            st.plotly_chart(fig_bp, use_container_width=True)

        with tab_gluc:
            fig_gluc = px.scatter(
                df_v,
                x="recorded_at",
                y="blood_glucose_mg_dl",
                color="glucose_context",
                title="Blood Glucose Measurements (mg/dL)",
                labels={"blood_glucose_mg_dl": "Glucose (mg/dL)", "recorded_at": "Timestamp"}
            )
            fig_gluc.add_hline(y=100, line_dash="dash", line_color="#f59e0b", annotation_text="Fasting Upper Normal (99)")
            fig_gluc.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor="#ffffff")
            st.plotly_chart(fig_gluc, use_container_width=True)

        with tab_temp:
            c_t1, c_t2 = st.columns(2)
            with c_t1:
                fig_t = px.line(df_v, x="recorded_at", y="temperature_f", markers=True, title="Body Temperature (°F)", color_discrete_sequence=["#f59e0b"])
                fig_t.add_hline(y=100.4, line_dash="dash", line_color="#ef4444", annotation_text="Fever Threshold")
                fig_t.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="#ffffff")
                st.plotly_chart(fig_t, use_container_width=True)
            with c_t2:
                fig_w = px.line(df_v, x="recorded_at", y="weight_kg", markers=True, title="Weight Tracking (kg)", color_discrete_sequence=["#10b981"])
                fig_w.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="#ffffff")
                st.plotly_chart(fig_w, use_container_width=True)

    else:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">💓</div>
            <div class="empty-state-title">{t('vitals_empty', lang)}</div>
            <p>Your interactive physiological trend graphs will populate here once recorded.</p>
        </div>
        """, unsafe_allow_html=True)

# Historical Records Table & Actions
st.markdown("---")
st.markdown(f"### 📋 {t('vitals_history_header', lang)}")

if vitals_history:
    table_data = []
    for v in vitals_history:
        status = v["flag_status"] or "Normal"
        badge = f"<span class='badge-danger'>{status}</span>" if status == "Urgent" else (f"<span class='badge-warning'>{status}</span>" if status == "Warning" else f"<span class='badge-normal'>{status}</span>")
        
        table_data.append({
            "ID": v["id"],
            "Timestamp": v["recorded_at"][:16],
            "BP (mmHg)": f"{v['systolic_bp']}/{v['diastolic_bp']}",
            "HR": f"{v['heart_rate']} BPM",
            "Temp": f"{v['temperature_f']:.1f}°F",
            "Glucose": f"{v['blood_glucose_mg_dl']:.0f} mg/dL ({v['glucose_context'] or 'Rand'})",
            "Weight": f"{v['weight_kg']} kg",
            "Status": badge,
            "Flag Reasons": v["flag_reasons"] or "Within standard limits",
            "Notes": v["notes"] or ""
        })

    df_table = pd.DataFrame(table_data)
    st.write(df_table.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Record Deletion Helper
    with st.expander("🗑️ Delete a specific vital entry"):
        del_id = st.selectbox("Select record ID to delete", [r["id"] for r in vitals_history])
        if st.button("Delete Selected Record", type="secondary"):
            database.delete_vital(del_id, user_id)
            st.success(f"Record #{del_id} deleted.")
            st.rerun()
else:
    st.info(t("vitals_empty", lang))

# Medical Disclaimer
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 2rem;">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)
