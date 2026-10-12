"""
pages/9_Health_Reports.py - Health Reports & Medical Document Storage Vault
Allows users to upload, securely store, preview, and download external medical PDFs & lab reports,
as well as generate consolidated PDF clinical summaries and raw CSV spreadsheets.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import database
import auth
import reports
from translations import t

st.set_page_config(page_title="Health Reports & Documents", page_icon="assets/logo.png", layout="wide")

auth.require_auth()

user_id = st.session_state.user_id
lang = st.session_state.get("lang", "en")

# Header
st.markdown(f"""
<div class="health-header">
    <h2>📑 {t('rep_title', lang)}</h2>
    <p>{t('rep_subtitle', lang)}</p>
</div>
""", unsafe_allow_html=True)

# Regulatory & Medical Notice
st.markdown(f"""
<div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 0.85rem 1.1rem; color: #166534; font-size: 0.86rem; margin-bottom: 1.25rem;">
    {t('rep_notice', lang)}
</div>
""", unsafe_allow_html=True)

# Overview Stats Card (5 dimensions)
v_count = len(database.get_vitals(user_id))
w_count = len(database.get_wellness_logs(user_id, days=365))
m_count = len(database.get_medicine_reminders(user_id, active_only=True))
a_count = len(database.get_appointments(user_id))
stored_docs = database.get_medical_documents(user_id)
d_count = len(stored_docs)

stat_html = (
    f'<div class="health-card">'
    f'<div style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; gap: 1rem;">'
    f'<div><div style="font-size: 1.8rem; font-weight: 700; color: #8b5cf6;">{d_count}</div><div style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Uploaded Reports (PDFs)</div></div>'
    f'<div><div style="font-size: 1.8rem; font-weight: 700; color: #0284c7;">{v_count}</div><div style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Vitals Records</div></div>'
    f'<div><div style="font-size: 1.8rem; font-weight: 700; color: #0d9488;">{w_count}</div><div style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Wellness Days Logged</div></div>'
    f'<div><div style="font-size: 1.8rem; font-weight: 700; color: #f59e0b;">{m_count}</div><div style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Active Prescriptions</div></div>'
    f'<div><div style="font-size: 1.8rem; font-weight: 700; color: #10b981;">{a_count}</div><div style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Consultation Visits</div></div>'
    f'</div>'
    f'</div>'
)
st.markdown(stat_html, unsafe_allow_html=True)

# Main Multi-Tab Interface
tab_vault, tab_export, tab_previews = st.tabs([
    f"📁 {t('doc_tab_storage', lang)} ({d_count})",
    f"📥 {t('doc_tab_exports', lang)}",
    f"👁️ {t('doc_tab_previews', lang)}"
])

# ==============================================================================
# TAB 1: UPLOAD & MEDICAL DOCUMENT STORAGE VAULT
# ==============================================================================
with tab_vault:
    col_upload, col_archive = st.columns([1.1, 1.4])

    with col_upload:
        with st.container(border=True):
            st.markdown(f"#### ➕ {t('doc_upload_header', lang)}")
            st.markdown("<p style='font-size: 0.83rem; color: #64748b;'>Upload diagnostic laboratory tests, blood work, radiology scan PDFs, or prescription slips to store them privately in your personal health locker.</p>", unsafe_allow_html=True)

            with st.form("upload_medical_doc_form", clear_on_submit=True):
                uploaded_file = st.file_uploader(
                    t("doc_file_label", lang),
                    type=["pdf", "png", "jpg", "jpeg", "txt"],
                    help="Supported formats: PDF, PNG, JPG, JPEG, TXT (Maximum file size: 25MB)"
                )

                doc_title = st.text_input(
                    t("doc_title_label", lang),
                    placeholder="e.g. Complete Blood Count (CBC) & Lipid Profile"
                )

                c_cat, c_date = st.columns(2)
                with c_cat:
                    cat_options = [
                        "Lab / Blood Test",
                        "Radiology / Scan (X-Ray, MRI, CT)",
                        "Doctor Prescription",
                        "Discharge Summary",
                        "Vaccination Record",
                        "Other Medical Document"
                    ]
                    doc_category = st.selectbox(t("doc_category_label", lang), cat_options)
                with c_date:
                    doc_date = st.date_input(t("doc_date_label", lang), value=date.today())

                doc_lab = st.text_input(
                    t("doc_lab_label", lang),
                    placeholder="e.g. Apollo Diagnostics, Dr. Lal PathLabs, Max Hospital"
                )

                doc_notes = st.text_area(
                    t("doc_notes_label", lang),
                    placeholder="e.g. Fasting blood sugar 94 mg/dL, HDL 52, LDL within normal reference range."
                )

                btn_upload = st.form_submit_button(
                    f"📤 {t('doc_save_btn', lang)}",
                    type="primary",
                    use_container_width=True
                )

                if btn_upload:
                    if not uploaded_file:
                        st.error("Please choose a PDF or image file to upload.")
                    elif not doc_title.strip():
                        st.error("Please provide a title for this medical document.")
                    else:
                        file_bytes = uploaded_file.read()
                        orig_name = uploaded_file.name
                        ext = os.path.splitext(orig_name)[1].lower()
                        file_type = ext.replace(".", "").upper()
                        file_size_kb = round(len(file_bytes) / 1024.0, 1)

                        user_upload_dir = database.get_user_upload_dir(user_id)
                        safe_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                        safe_clean = "".join(c for c in orig_name if c.isalnum() or c in (".", "_", "-")).strip()
                        saved_filename = f"report_{safe_time}_{safe_clean}"
                        saved_file_path = os.path.join(user_upload_dir, saved_filename)

                        with open(saved_file_path, "wb") as f:
                            f.write(file_bytes)

                        database.add_medical_document(
                            user_id=user_id,
                            title=doc_title,
                            category=doc_category,
                            report_date=doc_date,
                            doctor_or_lab=doc_lab,
                            file_name=orig_name,
                            file_path=saved_file_path,
                            file_size_kb=file_size_kb,
                            file_type=file_type,
                            notes=doc_notes
                        )
                        st.success(f"✅ {t('doc_upload_success', lang)}")
                        st.rerun()

    with col_archive:
        with st.container(border=True):
            st.markdown(f"#### 📁 {t('doc_tab_storage', lang)}")

            # Category filter & search bar
            f_col1, f_col2 = st.columns([1.1, 1.1])
            with f_col1:
                cat_choices = [
                    "All Reports",
                    "Lab / Blood Test",
                    "Radiology / Scan (X-Ray, MRI, CT)",
                    "Doctor Prescription",
                    "Discharge Summary",
                    "Vaccination Record",
                    "Other Medical Document"
                ]
                selected_cat = st.selectbox("Filter Category:", cat_choices, key="filter_doc_cat")
            with f_col2:
                search_query = st.text_input("🔍 Search Reports:", placeholder="Filter by title or lab...", key="search_doc_text")

            # Fetch stored documents
            cat_filter_param = None if selected_cat == "All Reports" else selected_cat
            filtered_docs = database.get_medical_documents(user_id, category_filter=cat_filter_param)

            if search_query.strip():
                sq = search_query.strip().lower()
                filtered_docs = [
                    d for d in filtered_docs
                    if sq in d["title"].lower() or (d["doctor_or_lab"] and sq in d["doctor_or_lab"].lower()) or (d["notes"] and sq in d["notes"].lower())
                ]

            if filtered_docs:
                for doc in filtered_docs:
                    doc_id = doc["id"]
                    f_type = doc["file_type"]
                    icon = "📄" if f_type == "PDF" else ("🖼️" if f_type in ("PNG", "JPG", "JPEG") else "📑")
                    lab_info = f" • 📍 {doc['doctor_or_lab']}" if doc["doctor_or_lab"] else ""
                    notes_html = f"<div style='font-size: 0.8rem; color: #475569; margin-top: 0.35rem; background: #f8fafc; padding: 0.4rem 0.6rem; border-radius: 6px;'>📝 <strong>Notes:</strong> {doc['notes']}</div>" if doc["notes"] else ""

                    card_doc_html = (
                        f'<div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #8b5cf6; border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.65rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">'
                        f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
                        f'<div>'
                        f'<div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">{icon} {doc["title"]}</div>'
                        f'<div style="font-size: 0.84rem; color: #64748b; margin-top: 0.2rem;">'
                        f'<span style="background: #f3e8ff; color: #7e22ce; padding: 2px 7px; border-radius: 9999px; font-weight: 600; font-size: 0.76rem;">{doc["category"]}</span>'
                        f' • 📅 <strong>{doc["report_date"]}</strong>{lab_info}'
                        f'</div>'
                        f'<div style="font-size: 0.78rem; color: #94a3b8; margin-top: 0.25rem;">File: <code>{doc["file_name"]}</code> ({doc["file_size_kb"]} KB • {f_type})</div>'
                        f'{notes_html}'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(card_doc_html, unsafe_allow_html=True)

                    # Action buttons: Download & Delete
                    act_c1, act_c2 = st.columns([1.5, 1])
                    with act_c1:
                        if os.path.exists(doc["file_path"]):
                            with open(doc["file_path"], "rb") as f_read:
                                file_content = f_read.read()
                            
                            mime_type = "application/pdf" if f_type == "PDF" else ("image/png" if f_type == "PNG" else ("image/jpeg" if f_type in ("JPG", "JPEG") else "application/octet-stream"))
                            st.download_button(
                                label=f"⬇️ Download {doc['file_name']}",
                                data=file_content,
                                file_name=doc["file_name"],
                                mime=mime_type,
                                key=f"dl_doc_{doc_id}",
                                use_container_width=True
                            )
                        else:
                            st.warning("Physical file not found on disk.")

                    with act_c2:
                        if st.button("🗑️ Delete Report", key=f"del_doc_{doc_id}", use_container_width=True):
                            database.delete_medical_document(doc_id, user_id)
                            st.info(t("doc_delete_success", lang))
                            st.rerun()

                    # In-App Preview Expander
                    with st.expander(f"👁️ View Document Preview ({doc['file_name']})"):
                        if os.path.exists(doc["file_path"]):
                            if f_type in ("PNG", "JPG", "JPEG"):
                                st.image(doc["file_path"], caption=doc["title"], use_container_width=True)
                            elif f_type == "TXT":
                                with open(doc["file_path"], "r", encoding="utf-8", errors="ignore") as txt_f:
                                    st.code(txt_f.read(), language="text")
                            elif f_type == "PDF":
                                st.info("📄 PDF Document ready. Click the download button above to view the full multi-page clinical report.")
                            else:
                                st.write(f"Binary file stored securely ({f_type}).")
                        else:
                            st.warning("File is missing from disk storage.")

            else:
                empty_doc_html = (
                    '<div class="empty-state">'
                    '<div class="empty-state-icon">📁</div>'
                    '<div class="empty-state-title">No Medical Documents Stored</div>'
                    f'<p>{t("doc_empty", lang)}</p>'
                    '</div>'
                )
                st.markdown(empty_doc_html, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: EXPORT CONSOLIDATED PDF & CSV SPREADSHEETS
# ==============================================================================
with tab_export:
    st.markdown("### 📥 Download Reports & Data")

    c_pdf, c_csv = st.columns([1.2, 1.8])

    with c_pdf:
        with st.container(border=True):
            st.markdown(
                '<h4 style="margin-top: 0; color: #0284c7;">📄 Consolidated PDF Report</h4>'
                '<p style="font-size: 0.85rem; color: #64748b;">'
                'Comprehensive printable health summary report including demographics, recent vital readings, '
                'ongoing medications, and upcoming appointments formatted for physician reviews.'
                '</p>',
                unsafe_allow_html=True
            )

            # Generate PDF in-memory bytes
            pdf_bytes = reports.generate_pdf_report(user_id)
            now_str = datetime.now().strftime("%Y%m%d_%H%M")

            st.download_button(
                label=f"⬇️ {t('rep_download_pdf', lang)}",
                data=pdf_bytes,
                file_name=f"Health_Summary_Report_{now_str}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

    with c_csv:
        with st.container(border=True):
            st.markdown(
                '<h4 style="margin-top: 0; color: #0d9488;">📊 Raw Data CSV Spreadsheets</h4>'
                '<p style="font-size: 0.85rem; color: #64748b;">'
                'Export your self-entered records into standard CSV format for spreadsheets or backup.'
                '</p>',
                unsafe_allow_html=True
            )

            csv_c1, csv_c2 = st.columns(2)

            with csv_c1:
                df_vit = reports.get_vitals_dataframe(user_id)
                if not df_vit.empty:
                    csv_v_bytes = df_vit.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📊 {t('rep_download_csv_vitals', lang)}",
                        data=csv_v_bytes,
                        file_name=f"vitals_records_{now_str}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("No Vitals to Export", disabled=True, use_container_width=True)

                df_med = reports.get_medicines_dataframe(user_id)
                if not df_med.empty:
                    csv_m_bytes = df_med.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"💊 {t('rep_download_csv_meds', lang)}",
                        data=csv_m_bytes,
                        file_name=f"medicine_reminders_{now_str}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("No Medications to Export", disabled=True, use_container_width=True)

            with csv_c2:
                df_wel = reports.get_wellness_dataframe(user_id)
                if not df_wel.empty:
                    csv_w_bytes = df_wel.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"🌱 {t('rep_download_csv_wellness', lang)}",
                        data=csv_w_bytes,
                        file_name=f"wellness_logs_{now_str}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("No Wellness Logs to Export", disabled=True, use_container_width=True)

                df_apt = reports.get_appointments_dataframe(user_id)
                if not df_apt.empty:
                    csv_a_bytes = df_apt.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📅 {t('rep_download_csv_apts', lang)}",
                        data=csv_a_bytes,
                        file_name=f"appointments_{now_str}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("No Appointments to Export", disabled=True, use_container_width=True)


# ==============================================================================
# TAB 3: IN-APP DATA PREVIEWS
# ==============================================================================
with tab_previews:
    st.markdown("### 👁️ In-App Record Previews")

    df_vit_p = reports.get_vitals_dataframe(user_id)
    df_wel_p = reports.get_wellness_dataframe(user_id)
    df_med_p = reports.get_medicines_dataframe(user_id)
    df_apt_p = reports.get_appointments_dataframe(user_id)

    tab_prev_vit, tab_prev_wel, tab_prev_med, tab_prev_apt = st.tabs([
        "💓 Vitals Records", "🌱 Wellness Logs", "💊 Prescriptions", "📅 Appointments"
    ])

    with tab_prev_vit:
        if not df_vit_p.empty:
            st.dataframe(df_vit_p, use_container_width=True, hide_index=True)
        else:
            st.info("No vitals records logged.")

    with tab_prev_wel:
        if not df_wel_p.empty:
            st.dataframe(df_wel_p, use_container_width=True, hide_index=True)
        else:
            st.info("No wellness records logged.")

    with tab_prev_med:
        if not df_med_p.empty:
            st.dataframe(df_med_p, use_container_width=True, hide_index=True)
        else:
            st.info("No medicine reminders logged.")

    with tab_prev_apt:
        if not df_apt_p.empty:
            st.dataframe(df_apt_p, use_container_width=True, hide_index=True)
        else:
            st.info("No appointments scheduled.")

# Global Medical Disclaimer
st.markdown(f"""
<div class="medical-disclaimer" style="margin-top: 2rem;">
    {t('medical_disclaimer', lang)}
</div>
""", unsafe_allow_html=True)
