"""
app.py - AI Powered Personal Health Copilot
Main entry point, authentication gateway, and central wellness hub.
"""

import streamlit as st
import importlib
import database
import auth
importlib.reload(auth)
from translations import t

# 1. Page Configuration
st.set_page_config(
    page_title="AI Powered Personal Health Copilot",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Session & Style Initialization
auth.init_session()
auth.inject_custom_css()
auth.render_sidebar()

lang = st.session_state.get("lang", "en")


def _get_app_logo_b64() -> str:
    """Safe retriever for base64 app logo with direct fallback."""
    if hasattr(auth, "get_logo_base64"):
        try:
            return auth.get_logo_base64()
        except Exception:
            pass
    import os, base64
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""


logo_b64 = _get_app_logo_b64()
logo_header_tag = f'<img src="data:image/png;base64,{logo_b64}" class="app-logo-badge" width="68" height="68" alt="Logo">' if logo_b64 else '🏥'

# 3. Main Header Banner
st.markdown(f"""
<div class="health-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
        <div style="display: flex; align-items: center; gap: 1.25rem;">
            {logo_header_tag}
            <div>
                <h1 style="font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;">{t('app_title', lang)}</h1>
                <p style="margin: 0.25rem 0 0 0; opacity: 0.95; font-size: 0.95rem;">{t('app_subtitle', lang)}</p>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.18); backdrop-filter: blur(8px); padding: 0.5rem 1rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.25);">
            🛡️ Private • Rule-Based • No Paid API Required
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. India Emergency Banner
st.markdown(f"""
<div class="emergency-banner">
    <div class="emergency-title">
        {t('emergency_banner_title', lang)}
    </div>
    <div style="font-size: 0.9rem; line-height: 1.4;">
        {t('emergency_banner_text', lang)}
    </div>
    <div class="emergency-phone">
        {t('emergency_call_btn', lang)}
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Check Authentication Status
if st.session_state.get("authenticated"):
    # Authenticated User Welcome Portal
    st.markdown(f"""
    <div class="health-card">
        <h3 style="margin: 0; color: #0284c7;">
            {t('dash_welcome', lang)}, {st.session_state.full_name}! 👋
        </h3>
        <p style="margin: 0.35rem 0 0 0; color: #64748b;">
            {t('dash_overview', lang)} Use the sidebar or quick links below to navigate your health copilot.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 🚀 {t('dash_quick_actions', lang)}")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-title">Overview</div>
            <div style="font-size: 1.15rem; font-weight: 700;">Personal Health Dashboard</div>
            <div class="metric-sub">Habit scores, vitals summaries & weekly charts</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_Dashboard.py", label=f"👉 {t('nav_dashboard', lang)}", use_container_width=True)

        st.markdown("""
        <div class="metric-box teal" style="margin-top: 1rem;">
            <div class="metric-title">Vitals</div>
            <div style="font-size: 1.15rem; font-weight: 700;">Vitals & Anomaly Tracker</div>
            <div class="metric-sub">Log BP, Heart Rate, Glucose & Temperature</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_Vitals_Tracker.py", label=f"👉 {t('nav_vitals', lang)}", use_container_width=True)

        st.markdown("""
        <div class="metric-box amber" style="margin-top: 1rem;">
            <div class="metric-title">Prescriptions</div>
            <div style="font-size: 1.15rem; font-weight: 700;">Medicine Reminders</div>
            <div class="metric-sub">Daily dose tracker & schedule reminders</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/6_Medicine_Reminders.py", label=f"👉 {t('nav_medicines', lang)}", use_container_width=True)

    with c2:
        st.markdown("""
        <div class="metric-box emerald">
            <div class="metric-title">Profile</div>
            <div style="font-size: 1.15rem; font-weight: 700;">Health Profile & Baseline</div>
            <div class="metric-sub">Age, height, weight, BMI & emergency contact</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_Health_Profile.py", label=f"👉 {t('nav_profile', lang)}", use_container_width=True)

        st.markdown("""
        <div class="metric-box" style="margin-top: 1rem;">
            <div class="metric-title">Assistant</div>
            <div style="font-size: 1.15rem; font-weight: 700;">AI Health Assistant</div>
            <div class="metric-sub">Rule-based lifestyle guidance & health literacy</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/4_AI_Health_Assistant.py", label=f"👉 {t('nav_assistant', lang)}", use_container_width=True)

        st.markdown("""
        <div class="metric-box teal" style="margin-top: 1rem;">
            <div class="metric-title">Consultations</div>
            <div style="font-size: 1.15rem; font-weight: 700;">Doctor Appointments</div>
            <div class="metric-sub">Track clinic visits & doctor notes</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/7_Appointments.py", label=f"👉 {t('nav_appointments', lang)}", use_container_width=True)

    with c3:
        st.markdown("""
        <div class="metric-box rose">
            <div class="metric-title">Safety</div>
            <div style="font-size: 1.15rem; font-weight: 700;">Symptom Checker & Triage</div>
            <div class="metric-sub">Red flag detection & safe first-step guidance</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/5_Symptom_Checker.py", label=f"👉 {t('nav_symptoms', lang)}", use_container_width=True)

        st.markdown("""
        <div class="metric-box amber" style="margin-top: 1rem;">
            <div class="metric-title">Daily Habits</div>
            <div style="font-size: 1.15rem; font-weight: 700;">Daily Wellness Tracker</div>
            <div class="metric-sub">Log hydration, sleep hours & exercise</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/8_Wellness_Tracker.py", label=f"👉 {t('nav_wellness', lang)}", use_container_width=True)

        st.markdown("""
        <div class="metric-box emerald" style="margin-top: 1rem;">
            <div class="metric-title">Exports</div>
            <div style="font-size: 1.15rem; font-weight: 700;">Health Reports Center</div>
            <div class="metric-sub">Consolidated PDF report & CSV downloads</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/9_Health_Reports.py", label=f"👉 {t('nav_reports', lang)}", use_container_width=True)

else:
    # Unauthenticated Landing & Authentication Portal
    logo_hero_tag = f'<img src="data:image/png;base64,{logo_b64}" class="app-logo-badge" width="96" height="96" alt="Logo" style="margin-bottom: 0.85rem;">' if logo_b64 else '🏥'
    st.markdown(f"""
    <div class="health-card" style="text-align: center; padding: 2.25rem 1.5rem;">
        {logo_hero_tag}
        <h2 style="color: #0284c7; margin: 0 0 0.5rem 0; font-weight: 800;">{t('auth_welcome', lang)}</h2>
        <p style="color: #64748b; max-width: 650px; margin: 0 auto 0.75rem auto; font-size: 0.95rem;">
            Securely track your personal vitals, daily hydration, sleep habits, prescription reminders, clinic appointments, and medical PDF reports in one private AI-assisted dashboard.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_auth, col_info = st.columns([1.1, 0.9])

    with col_auth:
        with st.container(border=True):
            login_tab, register_tab = st.tabs([f"🔑 {t('auth_login_tab', lang)}", f"📝 {t('auth_register_tab', lang)}"])

            with login_tab:
                with st.form("main_login_form"):
                    u_name = st.text_input(t("auth_username", lang), key="main_u")
                    u_pass = st.text_input(t("auth_password", lang), type="password", key="main_p")
                    submit_btn = st.form_submit_button(t("auth_login_btn", lang), type="primary", use_container_width=True)
                    
                    if submit_btn:
                        user, msg = auth.authenticate_user(u_name, u_pass)
                        if user:
                            auth.login(user)
                            st.success(t("auth_login_success", lang))
                            st.rerun()
                        else:
                            st.error(t("auth_invalid_credentials", lang))

                # Demo Instant Login Button
                st.markdown("<div style='text-align: center; margin: 0.8rem 0; color: #94a3b8; font-size: 0.85rem;'>— OR QUICK EVALUATION —</div>", unsafe_allow_html=True)
                if st.button("🚀 Quick Demo Login (Preloaded Data)", use_container_width=True, help="Instantly signs in as demo user with preloaded health records"):
                    demo_user = database.get_user_by_username("demo_user")
                    if not demo_user:
                        auth.register_user("demo_user", "password123", "Demo Health User", "demo@healthcopilot.local")
                        demo_user = database.get_user_by_username("demo_user")
                        database.seed_demo_data(demo_user["id"])
                    auth.login(dict(demo_user))
                    st.rerun()

            with register_tab:
                with st.form("main_reg_form"):
                    r_full = st.text_input(t("auth_fullname", lang), key="main_reg_name")
                    r_user = st.text_input(t("auth_username", lang), key="main_reg_user")
                    r_email = st.text_input(t("auth_email", lang), key="main_reg_email")
                    r_p1 = st.text_input(t("auth_password", lang), type="password", key="main_reg_p1")
                    r_p2 = st.text_input(t("auth_confirm_password", lang), type="password", key="main_reg_p2")
                    reg_btn = st.form_submit_button(t("auth_register_btn", lang), type="primary", use_container_width=True)
                    
                    if reg_btn:
                        if r_p1 != r_p2:
                            st.error(t("auth_password_mismatch", lang))
                        elif len(r_p1) < 6:
                            st.error(t("auth_password_short", lang))
                        else:
                            ok, reg_msg = auth.register_user(r_user, r_p1, r_full, r_email)
                            if ok:
                                new_user = database.get_user_by_username(r_user)
                                database.seed_demo_data(new_user["id"])
                                st.success(t("auth_register_success", lang))
                            else:
                                st.error(reg_msg)

    with col_info:
        st.markdown(f"""
        <div class="health-card">
            <h4 style="color: #0d9488; margin-top: 0;">✨ Core Capabilities</h4>
            <ul style="color: #475569; font-size: 0.9rem; padding-left: 1.2rem; line-height: 1.7;">
                <li><strong>Parameterized SQLite Database:</strong> Strict user-isolated health records with no shared access.</li>
                <li><strong>Physiological Vitals Tracker:</strong> Automatic reference check flagging elevated readings without diagnosing.</li>
                <li><strong>Transparent Health Habit Score:</strong> 0–100 score breaking down water, sleep, exercise, and meds adherence.</li>
                <li><strong>Rule-Based AI Assistant:</strong> Transparent, non-hallucinating health literacy with verified guidelines.</li>
                <li><strong>Emergency 112 Triage:</strong> Immediate recognition of acute symptoms with India helpline routing.</li>
                <li><strong>PDF & CSV Reports:</strong> Print-ready clinical summary exports for doctor appointments.</li>
                <li><strong>English & Telugu:</strong> Complete localization across all modules.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 6. Global Medical Disclaimer
st.markdown(f"""
<div class="medical-disclaimer">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    import sys
    from streamlit import runtime
    if not runtime.exists():
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())

