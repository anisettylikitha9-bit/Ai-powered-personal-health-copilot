"""
pages/5_Symptom_Checker.py - Symptom Checker & Emergency Triage Guide
Collects symptoms, duration, and severity. Recognizes critical red flags,
prominently routes to India 112 helpline, and provides safe educational self-care.
Strictly non-diagnostic.
"""

import streamlit as st
import pandas as pd
import database
import auth
from symptom_checker import assess_symptoms, RED_FLAG_SYMPTOMS, COMMON_SYMPTOMS_LIST, DURATION_CHOICES, SEVERITY_CHOICES
from translations import t

st.set_page_config(page_title="Symptom Checker", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")

# Header
st.markdown(f"""
<div class="health-header">
    <h2>🩺 {t('symp_title', lang)}</h2>
    <p>{t('symp_subtitle', lang)}</p>
</div>
""", unsafe_allow_html=True)

# Non-diagnostic banner
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 0; margin-bottom: 1.25rem;">
    <strong>ℹ️ Notice:</strong> {t('symp_disclaimer_modal', lang)}
</div>
""", unsafe_allow_html=True)

col_input, col_result = st.columns([1.1, 1.4])

with col_input:
    with st.container(border=True):
        st.markdown("#### 📝 Describe Your Symptoms")

        with st.form("symptom_assessment_form"):
            # Emergency Red Flag Section Notice
            st.markdown("<p style='font-size: 0.82rem; color: #b91c1c; font-weight: 600;'>🚨 If you have any red-flag symptoms below, select them immediately for urgent triage advice:</p>", unsafe_allow_html=True)
            selected_red_flags = st.multiselect("Critical Emergency Warning Signs:", RED_FLAG_SYMPTOMS)

            st.markdown("<p style='font-size: 0.85rem; color: #475569; font-weight: 600; margin-top: 0.8rem;'>Common Symptoms:</p>", unsafe_allow_html=True)
            selected_common = st.multiselect(t("symp_select", lang), COMMON_SYMPTOMS_LIST)

            c1, c2 = st.columns(2)
            with c1:
                duration = st.selectbox(t("symp_duration", lang), DURATION_CHOICES)
            with c2:
                severity = st.selectbox(t("symp_severity", lang), SEVERITY_CHOICES)

            notes = st.text_area(t("symp_additional_info", lang), placeholder="e.g., Symptoms worsen after meals; took a paracetamol 4 hours ago")

            submit_btn = st.form_submit_button(t("symp_check_btn", lang), type="primary", use_container_width=True)

with col_result:
    if submit_btn:
        all_selected = selected_red_flags + selected_common
        if not all_selected and not notes:
            st.warning("Please select at least one symptom or describe your symptoms in the notes.")
        else:
            assessment = assess_symptoms(all_selected, duration, severity, notes)
            
            # Save to database
            guidance_summary = "EMERGENCY DETECTED" if assessment["is_emergency"] else "; ".join(assessment.get("doctor_advice", []))
            database.log_symptom(
                user_id=user_id,
                symptoms=", ".join(all_selected) if all_selected else "Described in notes",
                duration=duration,
                severity=severity,
                is_emergency=1 if assessment["is_emergency"] else 0,
                guidance_summary=guidance_summary
            )

            if assessment["is_emergency"]:
                st.markdown(f"""
                <div class="emergency-banner">
                    <div class="emergency-title">
                        {assessment['headline']}
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #b91c1c; margin: 0.5rem 0;">
                        ⚠️ Warning Signs Identified: {', '.join(assessment['emergency_reasons'])}
                    </div>
                    <p style="margin: 0.5rem 0;">
                        This situation may require urgent medical assessment. Do not hesitate or delay.
                    </p>
                    <div class="emergency-phone">
                        📞 {assessment['emergency_number']}
                    </div>
                    <div style="margin-top: 1rem;">
                        <strong>Immediate Actions:</strong>
                        <ul style="margin: 0.5rem 0 0 1.2rem; font-size: 0.92rem;">
                            {''.join([f'<li>{action}</li>' for action in assessment['urgent_actions']])}
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.container(border=True):
                    st.markdown(f"<h4 style='color: #0f766e; margin-top:0;'>✅ {assessment['headline']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #64748b; font-size: 0.85rem;'>{assessment['severity_summary']}</p>", unsafe_allow_html=True)

                    st.markdown("##### 💧 Home Self-Care & Monitoring")
                    for tip in assessment["self_care_tips"]:
                        st.markdown(f"• {tip}")

                    st.markdown("##### 🩺 Recommended Next Steps & Medical Consultation")
                    for adv in assessment["doctor_advice"]:
                        st.markdown(f"• **{adv}**")

                    disc_html = (
                        '<div style="background: #f8fafc; border-radius: 8px; padding: 0.75rem; margin-top: 1rem; font-size: 0.8rem; color: #64748b;">'
                        f'{assessment["disclaimer"]}'
                        '</div>'
                    )
                    st.markdown(disc_html, unsafe_allow_html=True)
    else:
        with st.container(border=True):
            st.markdown(
                '<div style="text-align: center; padding: 2rem 1rem;">'
                '<div style="font-size: 2.8rem; margin-bottom: 0.5rem;">🩺 📋</div>'
                '<h4 style="color: #0284c7; margin-bottom: 0.25rem;">Triage & Guidance Engine</h4>'
                '<p style="color: #64748b; max-width: 450px; margin: 0 auto;">'
                'Select your symptoms on the left to receive structured educational guidance, safety checks, and emergency red-flag screening.'
                '</p>'
                '</div>',
                unsafe_allow_html=True
            )

# Past Symptom Checks Table
st.markdown("---")
st.markdown("### 📜 Past Symptom Check Sessions")

history = database.get_symptom_logs(user_id, limit=10)
if history:
    s_rows = []
    for h in history:
        is_em = h["is_emergency"] == 1
        st_badge = "<span class='badge-danger'>🚨 Emergency Flag</span>" if is_em else "<span class='badge-normal'>Safe Next Steps</span>"
        s_rows.append({
            "Date Logged": h["logged_at"][:16],
            "Symptoms": h["symptoms"],
            "Severity": h["severity"][:15],
            "Duration": h["duration"],
            "Triage Status": st_badge,
            "Guidance": h["guidance_summary"]
        })
    df_symp = pd.DataFrame(s_rows)
    st.write(df_symp.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.info("No symptom checks logged yet.")

# Global Medical Disclaimer
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 2rem;">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)
