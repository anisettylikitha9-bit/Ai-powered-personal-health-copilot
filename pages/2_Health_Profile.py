"""
pages/2_Health_Profile.py - Health Profile Management & Data Privacy
Maintains baseline demographic parameters, calculated BMI, emergency contacts,
and offers complete record deletion and account removal.
"""

import streamlit as st
import database
import auth
from wellness_engine import calculate_bmi
from translations import t

st.set_page_config(page_title="Personal Health Profile", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")

# Header
st.markdown(f"""
<div class="health-header">
    <h2>👤 {t('prof_title', lang)}</h2>
    <p>{t('prof_subtitle', lang)}</p>
</div>
""", unsafe_allow_html=True)

# Fetch existing profile
profile = database.get_profile(user_id)
current_user = database.get_user_by_id(user_id)

col_form, col_summary = st.columns([1.6, 1.0])

with col_form:
    with st.container(border=True):
        st.markdown(f"#### 📝 Baseline Health Parameters")

    with st.form("health_profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            p_age = st.number_input(
                t("prof_age", lang),
                min_value=1,
                max_value=120,
                value=int(profile["age"]) if profile and profile["age"] else 30,
                step=1
            )
            gender_options = ["Male", "Female", "Non-Binary / Other", "Prefer not to say"]
            p_curr_gender = profile["gender"] if profile and profile["gender"] in gender_options else "Male"
            p_gender = st.selectbox(
                t("prof_gender", lang),
                gender_options,
                index=gender_options.index(p_curr_gender)
            )
            p_height = st.number_input(
                t("prof_height", lang),
                min_value=50.0,
                max_value=250.0,
                value=float(profile["height_cm"]) if profile and profile["height_cm"] else 170.0,
                step=0.5
            )

        with c2:
            p_weight = st.number_input(
                t("prof_weight", lang),
                min_value=20.0,
                max_value=300.0,
                value=float(profile["weight_kg"]) if profile and profile["weight_kg"] else 70.0,
                step=0.5
            )
            bg_options = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-", "Unknown"]
            p_curr_bg = profile["blood_group"] if profile and profile["blood_group"] in bg_options else "O+"
            p_bg = st.selectbox(
                t("prof_blood_group", lang),
                bg_options,
                index=bg_options.index(p_curr_bg)
            )

        st.markdown("---")
        st.markdown(f"#### 🚨 Emergency Contact Information")
        c3, c4 = st.columns(2)
        with c3:
            p_em_name = st.text_input(
                t("prof_em_name", lang),
                value=profile["emergency_contact_name"] if profile and profile["emergency_contact_name"] else ""
            )
        with c4:
            p_em_phone = st.text_input(
                t("prof_em_phone", lang),
                value=profile["emergency_contact_phone"] if profile and profile["emergency_contact_phone"] else ""
            )

        st.markdown("---")
        st.markdown(f"#### 📋 Clinical Background & Ongoing Care")
        p_allergies = st.text_input(
            t("prof_allergies", lang),
            value=profile["allergies"] if profile and profile["allergies"] else "",
            placeholder="e.g., Penicillin, Peanuts, Pollen"
        )
        p_conditions = st.text_area(
            t("prof_conditions", lang),
            value=profile["chronic_conditions"] if profile and profile["chronic_conditions"] else "",
            placeholder="e.g., Mild Asthma, Stage 1 Hypertension"
        )
        p_meds = st.text_area(
            t("prof_meds", lang),
            value=profile["medications_summary"] if profile and profile["medications_summary"] else "",
            placeholder="e.g., Daily multivitamin, Inhaler as needed"
        )

        btn_save = st.form_submit_button(t("prof_save_btn", lang), type="primary", use_container_width=True)

        if btn_save:
            database.save_profile(
                user_id=user_id,
                age=int(p_age),
                gender=p_gender,
                height_cm=float(p_height),
                weight_kg=float(p_weight),
                blood_group=p_bg,
                emergency_contact_name=p_em_name,
                emergency_contact_phone=p_em_phone,
                allergies=p_allergies,
                chronic_conditions=p_conditions,
                medications_summary=p_meds
            )
            st.success(t("prof_saved_success", lang))
            st.rerun()

with col_summary:
    with st.container(border=True):
        st.markdown(f"#### 📊 Profile Metrics")

        # BMI Calculator Display
        bmi_info = calculate_bmi(
            profile["weight_kg"] if profile and profile["weight_kg"] else None,
            profile["height_cm"] if profile and profile["height_cm"] else None
        )

        if bmi_info:
            st.markdown(
                f'<div class="metric-box emerald">'
                f'<div class="metric-title">{t("dash_bmi", lang)}</div>'
                f'<div class="metric-value">{bmi_info["bmi"]}</div>'
                f'<div class="metric-sub"><span class="{bmi_info["badge_class"]}">{bmi_info["category"]}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="font-size: 0.8rem; color: #64748b; line-height: 1.4; margin-top: 0.5rem;">'
                'Healthy BMI range for adults is typically 18.5 – 24.9. Note that BMI does not differentiate between muscle mass and fat tissue.'
                '</p>',
                unsafe_allow_html=True
            )
        else:
            st.info("Save your height and weight to calculate your Body Mass Index (BMI).")

        st.markdown("---")
        st.markdown(f"#### 👤 Account Details")
        u_name = current_user['username'] if current_user else ''
        u_full = current_user['full_name'] if current_user else ''
        u_mail = current_user['email'] if current_user and current_user['email'] else 'Not specified'
        u_date = current_user['created_at'][:10] if current_user and current_user['created_at'] else 'Today'
        st.markdown(
            f'• **Username:** `@{u_name}`<br>'
            f'• **Full Name:** {u_full}<br>'
            f'• **Email:** {u_mail}<br>'
            f'• **Member Since:** {u_date}',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown(f"#### 🗑️ Clear Profile")
        if st.button(t("prof_delete_btn", lang), use_container_width=True):
            database.clear_profile(user_id)
            st.warning(t("prof_cleared_success", lang))
            st.rerun()

    # Danger Zone: Account Deletion
    with st.container(border=True):
        st.markdown(f"<h5 style='color: #b91c1c; margin-top: 0;'>⚠️ {t('prof_danger_zone', lang)}</h5>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 0.82rem; color: #991b1b;'>This action permanently wipes your user profile, vital signs, reminders, appointments, and wellness history from the SQLite database. This cannot be undone.</p>", unsafe_allow_html=True)
        
        confirm_box = st.checkbox(t("prof_confirm_delete", lang), key="delete_acc_check")
        if st.button(t("prof_delete_account", lang), type="secondary", disabled=not confirm_box, use_container_width=True):
            database.delete_user(user_id)
            auth.logout()

# Global Disclaimer
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 1.5rem;">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)
