"""
auth.py - Authentication, Password Hashing & Session Security Layer
Uses standard library hashlib PBKDF2-HMAC-SHA256 with cryptographically
random salts for secure zero-external-dependency password hashing.
"""

import hashlib
import secrets
import os
import base64
import streamlit as st
from typing import Optional, Tuple, Dict, Any
import database
from translations import t

HASH_ITERATIONS = 100_000


def get_logo_base64() -> str:
    """Returns base64-encoded string of the creative app logo for inline rendering."""
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes password using PBKDF2-HMAC-SHA256 with a unique cryptographic salt."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS
    )
    return hashed_bytes.hex(), salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifies candidate password against stored hash with constant-time comparison."""
    candidate_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(candidate_hash, stored_hash)


def register_user(username: str, password: str, full_name: str, email: Optional[str] = None) -> Tuple[bool, str]:
    """Validates and registers a new user with secure password hash."""
    username = username.strip().lower()
    full_name = full_name.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if not full_name:
        return False, "Please enter your full name."

    pwd_hash, salt = hash_password(password)
    user_id = database.create_user(username, pwd_hash, salt, full_name, email)
    if not user_id:
        return False, "Username is already taken. Please choose another."

    return True, "Account registered successfully! You can now log in."


def authenticate_user(username: str, password: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Authenticates username and password against SQLite database."""
    username = username.strip().lower()
    user_row = database.get_user_by_username(username)
    if not user_row:
        return None, "Invalid username or password."

    if not verify_password(password, user_row["password_hash"], user_row["salt"]):
        return None, "Invalid username or password."

    return dict(user_row), "Success"


def init_session():
    """Initializes Streamlit session state keys if not already present."""
    database.init_db()
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "full_name" not in st.session_state:
        st.session_state.full_name = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []


def login(user_dict: Dict[str, Any]):
    """Sets session state for authenticated user."""
    st.session_state.authenticated = True
    st.session_state.user_id = user_dict["id"]
    st.session_state.username = user_dict["username"]
    st.session_state.full_name = user_dict["full_name"]
    st.session_state.email = user_dict.get("email") or ""


def logout():
    """Clears user session state and triggers a rerun."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = ""
    st.session_state.full_name = ""
    st.session_state.email = ""
    st.session_state.chat_messages = []
    st.rerun()


def inject_custom_css():
    """Injects professional healthcare styling into Streamlit view."""
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar():
    """Renders the common sidebar controls (language switcher, user info, demo loader, logout)."""
    lang = st.session_state.get("lang", "en")
    
    with st.sidebar:
        # Streamlit Native Logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                st.logo(logo_path, size="large", icon_image=logo_path)
            except Exception:
                pass

        # App branding card with Creative Logo
        logo_b64 = get_logo_base64()
        if logo_b64:
            logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" class="app-logo-sidebar" width="88" height="88" alt="Health Copilot Logo">'
        else:
            logo_img_tag = '<div style="font-size: 2.2rem;">🏥 💙</div>'

        st.markdown(f"""
        <div style="padding: 0.5rem 0 1rem 0; text-align: center;">
            {logo_img_tag}
            <h3 style="margin: 0.25rem 0 0.1rem 0; font-size: 1.18rem; color: #0284c7; font-weight: 800; letter-spacing: -0.01em;">
                {t('app_title', lang)}
            </h3>
            <p style="font-size: 0.78rem; color: #64748b; margin: 0; font-weight: 500;">
                {t('app_subtitle', lang)}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Language Selector
        lang_options = {"English": "en", "తెలుగు (Telugu)": "te"}
        current_idx = 0 if lang == "en" else 1
        selected_lang_label = st.selectbox(
            f"🌐 {t('nav_language', lang)}",
            list(lang_options.keys()),
            index=current_idx,
            key="sidebar_lang_selector"
        )
        selected_code = lang_options[selected_lang_label]
        if selected_code != lang:
            st.session_state.lang = selected_code
            st.rerun()

        # User Profile Badge & Quick Controls
        if st.session_state.get("authenticated"):
            st.markdown(f"""
            <div style="background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 10px; padding: 0.8rem; margin: 0.8rem 0;">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: #0f766e; font-weight: 700;">
                    {t('nav_user_menu', lang)}
                </div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #0f172a; margin-top: 0.2rem;">
                    👤 {st.session_state.full_name}
                </div>
                <div style="font-size: 0.8rem; color: #64748b;">
                    @{st.session_state.username}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Demo Data Loader
            if st.button(f"✨ {t('nav_demo_data', lang)}", use_container_width=True, help="Loads realistic vitals, wellness logs, appointments, and medicine reminders"):
                database.seed_demo_data(st.session_state.user_id)
                st.success("Sample demo data loaded successfully!")
                st.rerun()

            # Logout Button
            if st.button(f"🚪 {t('nav_logout', lang)}", use_container_width=True, type="secondary"):
                logout()

        # Emergency Helpline Footer in Sidebar
        st.markdown(f"""
        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 0.65rem; margin-top: 1.5rem; font-size: 0.78rem; color: #991b1b; text-align: center;">
            <strong>🚨 India Emergency:</strong><br>
            <strong>Call 112</strong> | Ambulance: <strong>108</strong>
        </div>
        """, unsafe_allow_html=True)


def require_auth() -> bool:
    """
    Ensures authentication, injects CSS, and renders sidebar.
    If unauthenticated, prompts the user to log in and stops further page execution.
    """
    init_session()
    inject_custom_css()
    render_sidebar()

    if not st.session_state.get("authenticated"):
        logo_b64 = get_logo_base64()
        logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" class="app-logo-badge" width="56" height="56" alt="Logo">' if logo_b64 else '🏥'
        
        st.markdown(f"""
        <div class="health-header">
            <div style="display: flex; align-items: center; gap: 1rem;">
                {logo_img_tag}
                <div>
                    <h2 style="margin: 0; font-weight: 800;">{t('app_title', lang)}</h2>
                    <p style="margin: 0.2rem 0 0 0; opacity: 0.92;">{t('app_subtitle', lang)}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.warning(f"🔒 {t('auth_invalid_credentials', lang) if False else 'Please log in or register to access this health feature.'}")
        
        # Inline login and register tabs
        login_tab, register_tab = st.tabs([f"🔑 {t('auth_login_tab', lang)}", f"📝 {t('auth_register_tab', lang)}"])
        
        with login_tab:
            with st.form("inline_login_form"):
                u_name = st.text_input(t("auth_username", lang), key="auth_inline_u")
                u_pass = st.text_input(t("auth_password", lang), type="password", key="auth_inline_p")
                submit_btn = st.form_submit_button(t("auth_login_btn", lang), type="primary", use_container_width=True)
                
                if submit_btn:
                    user, msg = authenticate_user(u_name, u_pass)
                    if user:
                        login(user)
                        st.success(t("auth_login_success", lang))
                        st.rerun()
                    else:
                        st.error(t("auth_invalid_credentials", lang))

        with register_tab:
            with st.form("inline_reg_form"):
                r_full = st.text_input(t("auth_fullname", lang), key="auth_inline_reg_name")
                r_user = st.text_input(t("auth_username", lang), key="auth_inline_reg_user")
                r_email = st.text_input(t("auth_email", lang), key="auth_inline_reg_email")
                r_p1 = st.text_input(t("auth_password", lang), type="password", key="auth_inline_reg_p1")
                r_p2 = st.text_input(t("auth_confirm_password", lang), type="password", key="auth_inline_reg_p2")
                reg_btn = st.form_submit_button(t("auth_register_btn", lang), type="primary", use_container_width=True)
                
                if reg_btn:
                    if r_p1 != r_p2:
                        st.error(t("auth_password_mismatch", lang))
                    elif len(r_p1) < 6:
                        st.error(t("auth_password_short", lang))
                    else:
                        ok, reg_msg = register_user(r_user, r_p1, r_full, r_email)
                        if ok:
                            st.success(t("auth_register_success", lang))
                        else:
                            st.error(reg_msg)

        st.stop()
        return False
    
    return True
