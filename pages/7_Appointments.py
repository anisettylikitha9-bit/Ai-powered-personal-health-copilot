"""
pages/7_Appointments.py - Doctor Consultations & Clinic Appointments
Manages scheduled physician visits, preparation notes, status updates, and clinic logs.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import database
import auth
from translations import t

st.set_page_config(page_title="Doctor Appointments", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")
today = date.today()

# Header
st.markdown(f"""
<div class="health-header">
    <h2>📅 {t('apt_title', lang)}</h2>
    <p>{t('apt_subtitle', lang)}</p>
</div>
""", unsafe_allow_html=True)

col_book, col_list = st.columns([1.1, 1.4])

with col_book:
    with st.container(border=True):
        st.markdown("#### ➕ Schedule Consultation")

        with st.form("book_appointment_form"):
            doc_name = st.text_input(t("apt_doctor", lang), placeholder="e.g. Dr. Priya Rao")
            c1, c2 = st.columns(2)
            with c1:
                specialty_list = [
                    "General Physician", "Cardiologist", "Endocrinologist (Diabetologist)",
                    "Pulmonologist", "Dermatologist", "Neurologist", "Gastroenterologist",
                    "Dentist", "Ophthalmologist (Eye)", "Orthopedic", "Psychiatrist / Therapist", "Other"
                ]
                doc_spec = st.selectbox(t("apt_specialty", lang), specialty_list)
                apt_date = st.date_input(t("apt_date", lang), value=today + timedelta(days=3))

            with c2:
                clinic = st.text_input(t("apt_clinic", lang), placeholder="e.g. Apollo Clinic, Max Hospital")
                apt_time = st.text_input(t("apt_time", lang), value="10:30 AM")

            notes = st.text_area(t("apt_notes", lang), placeholder="Questions to ask: Review recent blood pressure readings, check dosage adjustments, seasonal allergy symptoms")

            submit_btn = st.form_submit_button(t("apt_add_btn", lang), type="primary", use_container_width=True)

            if submit_btn:
                if not doc_name:
                    st.error("Please enter the doctor or clinic name.")
                else:
                    database.add_appointment(
                        user_id=user_id,
                        doctor_name=doc_name,
                        clinic_hospital=clinic,
                        specialty=doc_spec,
                        appointment_date=apt_date,
                        appointment_time=apt_time,
                        notes=notes
                    )
                    st.success(f"Appointment with {doc_name} scheduled for {apt_date}!")
                    st.rerun()

    # Consultation Preparation Checklist
    chk_html = (
        '<div class="health-card" style="font-size: 0.85rem; color: #475569; margin-top: 1rem;">'
        '<h5 style="color: #0284c7; margin-top: 0;">💡 Appointment Preparation Checklist</h5>'
        '• <strong>Print / Export Vitals Report:</strong> Download your PDF report from the Health Reports tab.<br>'
        '• <strong>Medication List:</strong> Bring your list of active prescriptions and supplements.<br>'
        '• <strong>Questions to Ask:</strong> Write down your 2–3 most urgent symptoms or health questions.<br>'
        '• <strong>Arrive Early:</strong> Arrive 15 minutes before scheduled time for registration.'
        '</div>'
    )
    st.markdown(chk_html, unsafe_allow_html=True)

with col_list:
    with st.container(border=True):
        st.markdown(f"#### 🗓️ {t('apt_upcoming', lang)}")

        upcoming_apts = database.get_appointments(user_id, status_filter="Scheduled")

        if upcoming_apts:
            for apt in upcoming_apts:
                a_id = apt["id"]
                apt_notes_html = f"<div style='font-size: 0.8rem; color: #64748b; font-style: italic; margin-top: 0.35rem;'>📝 Notes: {apt['notes']}</div>" if apt['notes'] else ""
                card_apt_html = (
                    f'<div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.85rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">'
                    f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
                    f'<div>'
                    f'<div style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">{apt["doctor_name"]}</div>'
                    f'<div style="font-size: 0.85rem; color: #0284c7; font-weight: 600;">{apt["specialty"] or "Specialist"} • 📍 {apt["clinic_hospital"] or "Clinic"}</div>'
                    f'<div style="font-size: 0.82rem; color: #475569; margin-top: 0.35rem;">'
                    f'📅 <strong>{apt["appointment_date"]}</strong> at <strong>{apt["appointment_time"]}</strong>'
                    f'</div>'
                    f'{apt_notes_html}'
                    f'</div>'
                    f'<span class="badge-info">Scheduled</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_apt_html, unsafe_allow_html=True)

                c_act1, c_act2, c_act3 = st.columns([1, 1, 1])
                with c_act1:
                    if st.button("✅ Mark Completed", key=f"apt_done_{a_id}", use_container_width=True):
                        database.update_appointment_status(a_id, user_id, "Completed")
                        st.success("Appointment marked as completed.")
                        st.rerun()
                with c_act2:
                    if st.button("❌ Cancel Visit", key=f"apt_cancel_{a_id}", use_container_width=True):
                        database.update_appointment_status(a_id, user_id, "Cancelled")
                        st.info("Appointment cancelled.")
                        st.rerun()
                with c_act3:
                    if st.button("🗑️ Delete Record", key=f"apt_del_{a_id}", use_container_width=True):
                        database.delete_appointment(a_id, user_id)
                        st.rerun()

        else:
            empty_apt_html = (
                '<div class="empty-state">'
                '<div class="empty-state-icon">📅</div>'
                '<div class="empty-state-title">No Consultations Scheduled</div>'
                '<p>Schedule your upcoming preventive checkup or specialist visit on the left.</p>'
                '</div>'
            )
            st.markdown(empty_apt_html, unsafe_allow_html=True)

# Appointment History Table
st.markdown("---")
st.markdown(f"### 📋 {t('apt_history', lang)}")

all_apts = database.get_appointments(user_id)
past_apts = [a for a in all_apts if a["status"] != "Scheduled"]

if past_apts:
    p_data = []
    for a in past_apts:
        st_color = "badge-normal" if a["status"] == "Completed" else "badge-danger"
        badge = f"<span class='{st_color}'>{a['status']}</span>"
        p_data.append({
            "Doctor": a["doctor_name"],
            "Specialty": a["specialty"] or "General",
            "Clinic / Hospital": a["clinic_hospital"] or "N/A",
            "Date": a["appointment_date"],
            "Time": a["appointment_time"],
            "Status": badge,
            "Notes": a["notes"] or ""
        })
    df_past = pd.DataFrame(p_data)
    st.write(df_past.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.info("No past appointment history records yet.")

# Global Medical Disclaimer
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 2rem;">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)
