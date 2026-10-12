"""
pages/4_AI_Health_Assistant.py - Upgraded Symptom-Aware AI Health Assistant
Interactive chat interface delivering transparent, symptom-aware health education,
emergency red-flag triage (India 112 / 108), and non-prescriptive medication guidance.
Strictly non-diagnostic and non-prescriptive.
"""

import streamlit as st
import importlib
import database
import auth
import health_assistant
importlib.reload(health_assistant)
from translations import t

st.set_page_config(page_title="AI Health Assistant", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")

# 1. Page Header Banner
st.markdown(f"""
<div class="health-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
        <div>
            <h2>🤖 {t('asst_title', lang)}</h2>
            <p>{t('asst_subtitle', lang)}</p>
        </div>
        <div style="background: rgba(255,255,255,0.2); padding: 0.4rem 0.85rem; border-radius: 20px; font-size: 0.82rem; font-weight: 600;">
            🛡️ Rule-Based • Symptom-Aware • Non-Diagnostic
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Prominent Safety Disclaimer Banner
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 0; margin-bottom: 1rem; border-left: 4px solid #0d9488;">
    <strong>⚕️ {t('medical_disclaimer', lang)}</strong><br>
    <span style="font-size: 0.8rem; color: #475569;">
        {t('asst_transparency_note', lang)}
    </span>
</div>
""", unsafe_allow_html=True)

# 3. Optional Structured Assessment Expander
with st.expander("📋 " + ("లక్షణాల నిర్మాణాత్మక తనిఖీ (ఐచ్ఛికం)" if lang == "te" else "Structured Symptom Assessment Helper (Optional)"), expanded=False):
    st.markdown(
        "<p style='font-size: 0.85rem; color: #64748b;'>"
        + ("మీ లక్షణాలను దశలవారీగా నమోదు చేసి అసిస్టెంట్‌తో విశ్లేషించవచ్చు:" if lang == "te" else "Quickly organize your symptoms with duration and severity to ask the assistant:")
        + "</p>",
        unsafe_allow_html=True
    )
    with st.form("quick_symptom_form"):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            symp_choices = [
                "Headache", "Fever", "Cough", "Sore throat", "Runny nose / Cold",
                "Stomach pain", "Dizziness / Weakness", "Trouble sleeping",
                "Body pain / Fatigue", "Nausea / Vomiting", "Diarrhea"
            ]
            f_main_symp = st.selectbox("Main Symptom:" if lang == "en" else "ప్రధాన లక్షణం:", symp_choices)
        with sc2:
            dur_choices = ["Less than 24 hours", "1 to 2 days", "3 to 5 days", "More than 1 week", "More than 2 weeks"]
            f_duration = st.selectbox("Duration:" if lang == "en" else "ఎంతకాలంగా ఉంది:", dur_choices)
        with sc3:
            sev_choices = ["Mild", "Moderate", "Severe"]
            f_severity = st.selectbox("Severity:" if lang == "en" else "తీవ్రత:", sev_choices)

        f_notes = st.text_input("Additional Symptoms or Notes:" if lang == "en" else "ఇతర వివరాలు లేదా లక్షణాలు:", placeholder="e.g. Mild nausea, slight fatigue")
        form_submit = st.form_submit_button("Ask Assistant with this Assessment" if lang == "en" else "ఈ వివరాలతో అసిస్టెంట్‌ను అడగండి", type="primary")

    if form_submit:
        structured_prompt = f"I have {f_main_symp.lower()} for {f_duration.lower()}, severity is {f_severity.lower()}."
        if f_notes:
            structured_prompt += f" Also experiencing: {f_notes}."
        st.session_state["pending_prompt"] = structured_prompt
        st.rerun()

# 4. Quick Suggestion Prompt Pills
st.markdown(f"**{'త్వరిత ప్రశ్నలు:' if lang == 'te' else t('asst_quick_topics', lang)}**")

if lang == "te":
    quick_prompts = [
        ("🤕 తలనొప్పి", "నాకు తలనొప్పిగా ఉంది."),
        ("🌡️ జ్వరం & గొంతు నొప్పి", "నాకు జ్వరం మరియు గొంతు నొప్పి ఉంది."),
        ("🤧 దగ్గు & జలుబు", "నాకు దగ్గు మరియు ముక్కు కారడం ఉంది."),
        ("🤢 కడుపు నొప్పి", "నాకు కడుపు నొప్పిగా ఉంది."),
        ("💫 కళ్ళు తిరగడం", "నాకు కళ్ళు తిరుగుతున్నాయి, నీరసంగా ఉంది."),
        ("🌙 నిద్రలేమి", "నాకు నిద్ర పట్టడం లేదు."),
        ("💊 ఏ టాబ్లెట్ వేసుకోవాలి?", "నాకు జ్వరం ఉంది, ఏ టాబ్లెట్ వేసుకోవాలి?")
    ]
else:
    quick_prompts = [
        ("🤕 Headache", "I have a headache."),
        ("🌡️ Fever & Sore Throat", "I have a fever and a sore throat."),
        ("🤧 Cough & Cold", "I have a cough and a runny nose."),
        ("🤢 Stomach Pain", "I have stomach pain."),
        ("💫 Dizzy & Weak", "I feel dizzy and weak."),
        ("🌙 Trouble Sleeping", "I have trouble sleeping."),
        ("💊 Which tablet should I take?", "Which tablet should I take?")
    ]

chip_cols = st.columns(len(quick_prompts))
clicked_prompt = None

for i, (label, prompt_text) in enumerate(quick_prompts):
    with chip_cols[i]:
        if st.button(label, key=f"quick_chip_{i}", use_container_width=True):
            clicked_prompt = prompt_text

# Check for pending prompt from structured form
if "pending_prompt" in st.session_state:
    clicked_prompt = st.session_state.pop("pending_prompt")

# 5. Load and Display Chat History
stored_messages = database.get_chat_history(user_id, limit=50)

chat_container = st.container()
with chat_container:
    if not stored_messages and not clicked_prompt:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-state-icon">🤖 💬</div>
            <div class="empty-state-title">
                {'మీ ఆరోగ్య లక్షణాలను అడగండి' if lang == 'te' else 'Symptom-Aware Assistant Ready'}
            </div>
            <p style="max-width: 550px; margin: 0 auto;">
                {'మీరు తలనొప్పి, జ్వరం, దగ్గు, కడుపు నొప్పి లేదా నిద్రలేమి వంటి లక్షణాలను సహజ భాషలో అడగవచ్చు. పైన ఉన్న త్వరిత బటన్లను క్లిక్ చేయండి లేదా క్రింద టైప్ చేయండి.' if lang == 'te' else 'Describe your symptoms in natural language (e.g. "I have a headache", "I have a fever and cough"), or ask about sleep, hydration, and vitals literacy.'}
            </p>
        </div>
        """, unsafe_allow_html=True)

    for msg in stored_messages:
        role = msg["role"]
        content = msg["content"]
        with st.chat_message(role, avatar="🧑" if role == "user" else "🤖"):
            st.markdown(content, unsafe_allow_html=True)

# 6. Chat Input Processing
input_placeholder = "లక్షణాలను టైప్ చేయండి (ఉదా: 'నాకు తలనొప్పిగా ఉంది')..." if lang == "te" else "Describe your symptoms (e.g. 'I have a fever and sore throat')..."
user_text = st.chat_input(input_placeholder)

prompt_to_handle = clicked_prompt if clicked_prompt else user_text

if prompt_to_handle:
    # 1. Save and display user message
    database.save_chat_message(user_id, "user", prompt_to_handle)
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt_to_handle)

    # 2. Generate response with spinner
    with st.spinner("Analyzing symptoms & safety guidelines..." if lang == "en" else "లక్షణాలు మరియు భద్రతా నియమాలను విశ్లేషిస్తోంది..."):
        response_data = health_assistant.get_assistant_response(prompt_to_handle, user_id=user_id, lang=lang)

    # 3. Format message with emergency or rule styling
    is_em = response_data.get("is_emergency", False)
    if is_em:
        formatted_reply = f"""<div class="emergency-banner" style="margin-bottom: 0.5rem;">
<div class="emergency-title">🚨 EMERGENCY SAFETY ALERT</div>
{response_data['content']}
</div>"""
    else:
        rule_badge = f"<span class='chat-rule-badge'>⚙️ {response_data['matched_rule']}</span><br><br>"
        formatted_reply = rule_badge + response_data["content"]

    # 4. Save and display assistant message
    database.save_chat_message(user_id, "assistant", formatted_reply)
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(formatted_reply, unsafe_allow_html=True)

    st.rerun()

# 7. Bottom Controls (Clear Chat & Emergency Helpline)
st.markdown("---")
c_clear, c_em = st.columns([1, 2])

with c_clear:
    if st.button(f"🗑️ {t('asst_clear_chat', lang)}", use_container_width=True):
        database.clear_chat_history(user_id)
        st.success("Conversation history cleared." if lang == "en" else "సంభాషణ చరిత్ర క్లియర్ చేయబడింది.")
        st.rerun()

with c_em:
    st.markdown(f"""
    <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.8rem; color: #991b1b; text-align: right;">
        🚨 <strong>India Emergency:</strong> Call <strong>112</strong> | Ambulance: <strong>108</strong>
    </div>
    """, unsafe_allow_html=True)
