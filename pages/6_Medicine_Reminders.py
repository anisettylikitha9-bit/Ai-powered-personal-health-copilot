"""
pages/6_Medicine_Reminders.py - Prescription & Medicine Reminders
Organizes user-entered prescription schedules and tracks daily adherence.
Strictly non-prescriptive; never recommends or alters medication dosages.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import database
import auth
from translations import t

st.set_page_config(page_title="Medicine Reminders", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")
today = date.today()

# Header
st.markdown(f"""
<div class="health-header">
    <h2>💊 {t('med_title', lang)}</h2>
    <p>{t('med_subtitle', lang)}</p>
</div>
""", unsafe_allow_html=True)

# Non-prescriptive notice
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 0; margin-bottom: 1.25rem;">
    {t('med_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)

col_add, col_today = st.columns([1.1, 1.4])

with col_add:
    with st.container(border=True):
        st.markdown("#### ➕ Add Prescribed Medication Reminder")

        with st.form("add_medicine_form"):
            med_name = st.text_input(t("med_name", lang), placeholder="e.g. Metformin, Multivitamin, Cetirizine")
            c1, c2 = st.columns(2)
            with c1:
                med_dose = st.text_input(t("med_dosage", lang), placeholder="e.g. 500mg, 1 Capsule")
                med_time = st.text_input(t("med_time", lang), value="08:30 AM")
            with c2:
                timing_options = ["Morning", "Afternoon", "Evening", "Night / Bedtime", "As Needed"]
                med_timing = st.selectbox(t("med_timing", lang), timing_options)
                med_start = st.date_input(t("med_start", lang), value=today)

            med_instructions = st.text_input(
                t("med_instructions", lang),
                placeholder="e.g. Take with warm water after food as prescribed by doctor"
            )
            
            has_end_date = st.checkbox("Set specific end date", value=False)
            med_end = None
            if has_end_date:
                med_end = st.date_input(t("med_end", lang), value=today + timedelta(days=30))

            add_btn = st.form_submit_button(t("med_add_btn", lang), type="primary", use_container_width=True)

            if add_btn:
                if not med_name or not med_dose:
                    st.error("Please enter both medicine name and dosage.")
                else:
                    database.add_medicine_reminder(
                        user_id=user_id,
                        medicine_name=med_name,
                        dosage=med_dose,
                        schedule_timing=med_timing,
                        time_str=med_time,
                        instructions=med_instructions,
                        start_date=med_start,
                        end_date=med_end if has_end_date else None
                    )
                    st.success(f"Reminder for '{med_name}' added successfully!")
                    st.rerun()

with col_today:
    with st.container(border=True):
        st.markdown(f"#### 📅 {t('med_today_header', lang)} ({today.strftime('%d %b %Y')})")

        active_reminders = database.get_medicine_reminders(user_id, active_only=True)
        completed_today = database.get_medicine_logs_for_date(user_id, today)

        if active_reminders:
            adherence_count = len(completed_today)
            total_count = len(active_reminders)
            adherence_pct = round((adherence_count / total_count) * 100) if total_count > 0 else 0
            adh_badge_class = "badge-normal" if adherence_pct == 100 else "badge-warning"
            adh_badge_text = "Completed" if adherence_pct == 100 else "In Progress"

            adherence_html = (
                f'<div style="background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 8px; padding: 0.6rem 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;">'
                f'<div style="font-size: 0.88rem; color: #0f766e; font-weight: 600;">'
                f"Today's Adherence: {adherence_count} of {total_count} Taken ({adherence_pct}%)"
                f'</div>'
                f'<span class="{adh_badge_class}">{adh_badge_text}</span>'
                f'</div>'
            )
            st.markdown(adherence_html, unsafe_allow_html=True)

            for med in active_reminders:
                m_id = med["id"]
                is_taken = m_id in completed_today
                inst_html = f"<div style='font-size: 0.8rem; color: #0d9488; margin-top: 0.25rem;'>📝 {med['instructions']}</div>" if med['instructions'] else ""
                badge_class = "badge-normal" if is_taken else "badge-warning"
                badge_text = ("✅ " + t("med_status_completed", lang)) if is_taken else ("⏳ " + t("med_status_pending", lang))
                border_col = "#86efac" if is_taken else "#e2e8f0"

                card_html = (
                    f'<div style="background: #ffffff; border: 1px solid {border_col}; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">'
                    f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
                    f'<div>'
                    f'<div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{med["medicine_name"]}</div>'
                    f'<div style="font-size: 0.85rem; color: #64748b; margin-top: 0.15rem;">'
                    f'<strong>{med["dosage"]}</strong> • <span style="color: #0284c7;">⏰ {med["time_str"]} ({med["schedule_timing"]})</span>'
                    f'</div>'
                    f'{inst_html}'
                    f'</div>'
                    f'<span class="{badge_class}">{badge_text}</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                btn_txt = "↩️ Undo (Mark as Pending)" if is_taken else "✔️ Mark as Taken"
                if st.button(f"{btn_txt} — {med['medicine_name']}", key=f"med_toggle_{m_id}"):
                    if is_taken:
                        database.unmark_medicine_taken(m_id, user_id, today)
                    else:
                        database.mark_medicine_taken(m_id, user_id, today)
                    st.rerun()

        else:
            st.markdown(
                '<div class="empty-state">'
                '<div class="empty-state-icon">💊</div>'
                '<div class="empty-state-title">No Medications Scheduled</div>'
                '<p>Add your prescribed daily medications on the left to activate reminders.</p>'
                '</div>',
                unsafe_allow_html=True
            )

# All Active Prescriptions Management
st.markdown("---")
st.markdown(f"### 📋 {t('med_all_reminders', lang)}")

all_meds = database.get_medicine_reminders(user_id, active_only=False)

if all_meds:
    m_data = []
    for m in all_meds:
        m_data.append({
            "ID": m["id"],
            "Medicine Name": m["medicine_name"],
            "Dosage": m["dosage"],
            "Timing": f"{m['time_str']} ({m['schedule_timing']})",
            "Doctor's Instructions": m["instructions"] or "None",
            "Start Date": m["start_date"] or "N/A",
            "End Date": m["end_date"] or "Ongoing",
            "Status": "Active" if m["is_active"] else "Inactive"
        })
    df_m = pd.DataFrame(m_data)
    st.dataframe(df_m, use_container_width=True, hide_index=True)

    with st.expander("🗑️ Delete a medicine reminder"):
        del_m_id = st.selectbox("Select medication to remove", [m["id"] for m in all_meds], format_func=lambda x: f"ID #{x} - {next((m['medicine_name'] for m in all_meds if m['id']==x), '')}")
        if st.button("Delete Medication Reminder", type="secondary"):
            database.delete_medicine_reminder(del_m_id, user_id)
            st.success("Medication reminder removed.")
            st.rerun()
else:
    st.info("No medicine records found.")

# Global Medical Disclaimer
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 2rem;">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)
