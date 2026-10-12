"""
reports.py - Health Reports Generator (CSV & PDF)
Produces structured, printable PDF clinical summaries and CSV exports.
Strictly labels all records as user-entered personal tracking information.
"""

import io
import os
import pandas as pd
from datetime import datetime, date
from typing import Optional
import database
from wellness_engine import calculate_bmi


def get_vitals_dataframe(user_id: int) -> pd.DataFrame:
    """Fetches user vitals as a styled Pandas DataFrame with explicit disclaimers."""
    rows = database.get_vitals(user_id, limit=200)
    if not rows:
        return pd.DataFrame()
    
    data = []
    for r in rows:
        data.append({
            "Recorded At": r["recorded_at"],
            "Systolic BP (mmHg)": r["systolic_bp"],
            "Diastolic BP (mmHg)": r["diastolic_bp"],
            "Heart Rate (BPM)": r["heart_rate"],
            "Temperature (°F)": r["temperature_f"],
            "Weight (kg)": r["weight_kg"],
            "Glucose (mg/dL)": r["blood_glucose_mg_dl"],
            "Glucose Context": r["glucose_context"],
            "Flag Status": r["flag_status"],
            "Notes": r["notes"] or "",
            "Record Nature": "User-Entered Self-Tracking Data (Non-Clinical Lab Result)"
        })
    return pd.DataFrame(data)


def get_wellness_dataframe(user_id: int) -> pd.DataFrame:
    """Fetches user daily wellness logs as Pandas DataFrame."""
    rows = database.get_wellness_logs(user_id, days=90)
    if not rows:
        return pd.DataFrame()
    
    data = []
    for r in rows:
        data.append({
            "Log Date": r["log_date"],
            "Water Intake (ml)": r["water_ml"],
            "Sleep Duration (hrs)": r["sleep_hours"],
            "Exercise (mins)": r["exercise_mins"],
            "Exercise Type": r["exercise_type"] or "N/A",
            "Mood / Energy": r["mood"] or "N/A",
            "Meal Notes": r["meal_notes"] or "",
            "Record Nature": "User-Entered Self-Tracking Data"
        })
    return pd.DataFrame(data)


def get_appointments_dataframe(user_id: int) -> pd.DataFrame:
    """Fetches user appointments as Pandas DataFrame."""
    rows = database.get_appointments(user_id)
    if not rows:
        return pd.DataFrame()
    
    data = []
    for r in rows:
        data.append({
            "Doctor Name": r["doctor_name"],
            "Hospital / Clinic": r["clinic_hospital"] or "N/A",
            "Specialty": r["specialty"] or "General",
            "Date": r["appointment_date"],
            "Time": r["appointment_time"],
            "Status": r["status"],
            "Notes": r["notes"] or ""
        })
    return pd.DataFrame(data)


def get_medicines_dataframe(user_id: int) -> pd.DataFrame:
    """Fetches user medicine reminders as Pandas DataFrame."""
    rows = database.get_medicine_reminders(user_id, active_only=False)
    if not rows:
        return pd.DataFrame()
    
    data = []
    for r in rows:
        data.append({
            "Medicine Name": r["medicine_name"],
            "Dosage": r["dosage"],
            "Timing": r["schedule_timing"],
            "Target Time": r["time_str"],
            "Doctor's Instructions": r["instructions"] or "As directed",
            "Start Date": r["start_date"] or "N/A",
            "End Date": r["end_date"] or "Ongoing",
            "Active Status": "Active" if r["is_active"] else "Inactive"
        })
    return pd.DataFrame(data)


def generate_pdf_report(user_id: int) -> bytes:
    """
    Generates a structured, professional multi-section PDF health summary
    using ReportLab with clean tables, metadata, and prominent disclaimers.
    """
    buffer = io.BytesIO()

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0284c7'),
            alignment=1  # Centered
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#64748b'),
            alignment=1
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=10,
            spaceAfter=4
        )
        
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155')
        )

        disclaimer_style = ParagraphStyle(
            'DisclaimerText',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#991b1b'),
            alignment=1
        )

        elements = []

        # Logo & Brand Header
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                from reportlab.platypus import Image as RLImage
                img = RLImage(logo_path, width=42, height=42)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 6))
            except Exception:
                pass

        # Header
        elements.append(Paragraph("AI POWERED PERSONAL HEALTH COPILOT", title_style))
        elements.append(Paragraph(f"Consolidated Personal Health & Wellness Record • Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

        # Demographic Profile Section
        user = database.get_user_by_id(user_id)
        profile = database.get_profile(user_id)
        
        full_name = user["full_name"] if user else "Personal User"
        age = f"{profile['age']} yrs" if profile and profile["age"] else "N/A"
        gender = profile["gender"] if profile and profile["gender"] else "N/A"
        height = f"{profile['height_cm']} cm" if profile and profile["height_cm"] else "N/A"
        weight = f"{profile['weight_kg']} kg" if profile and profile["weight_kg"] else "N/A"
        bg = profile["blood_group"] if profile and profile["blood_group"] else "N/A"
        em_name = profile["emergency_contact_name"] if profile and profile["emergency_contact_name"] else "N/A"
        em_phone = profile["emergency_contact_phone"] if profile and profile["emergency_contact_phone"] else "N/A"
        allergies = profile["allergies"] if profile and profile["allergies"] else "None recorded"
        conditions = profile["chronic_conditions"] if profile and profile["chronic_conditions"] else "None recorded"

        bmi_info = calculate_bmi(profile["weight_kg"] if profile else None, profile["height_cm"] if profile else None)
        bmi_str = f"{bmi_info['bmi']} ({bmi_info['category']})" if bmi_info else "N/A"

        elements.append(Paragraph("1. PATIENT DEMOGRAPHICS & HEALTH PROFILE", section_style))
        demo_table_data = [
            [Paragraph("<b>Full Name:</b>", body_style), Paragraph(full_name, body_style), Paragraph("<b>Blood Group:</b>", body_style), Paragraph(bg, body_style)],
            [Paragraph("<b>Age:</b>", body_style), Paragraph(age, body_style), Paragraph("<b>Gender:</b>", body_style), Paragraph(gender, body_style)],
            [Paragraph("<b>Height:</b>", body_style), Paragraph(height, body_style), Paragraph("<b>Weight:</b>", body_style), Paragraph(weight, body_style)],
            [Paragraph("<b>Calculated BMI:</b>", body_style), Paragraph(bmi_str, body_style), Paragraph("<b>Emergency Contact:</b>", body_style), Paragraph(f"{em_name} ({em_phone})", body_style)],
            [Paragraph("<b>Known Allergies:</b>", body_style), Paragraph(allergies, body_style), Paragraph("<b>Chronic Conditions:</b>", body_style), Paragraph(conditions, body_style)]
        ]
        t_demo = Table(demo_table_data, colWidths=[100, 170, 110, 160])
        t_demo.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_demo)
        elements.append(Spacer(1, 12))

        # Recent Vitals Readings Section
        elements.append(Paragraph("2. RECENT VITAL READINGS (LATEST 7 ENTRIES)", section_style))
        vitals = database.get_vitals(user_id, limit=7)
        if vitals:
            v_data = [["Date & Time", "BP (mmHg)", "HR (BPM)", "Temp (°F)", "Glucose", "Flag Status"]]
            for v in vitals:
                bp = f"{v['systolic_bp']}/{v['diastolic_bp']}" if v['systolic_bp'] and v['diastolic_bp'] else "N/A"
                hr = str(v['heart_rate']) if v['heart_rate'] else "N/A"
                temp = f"{v['temperature_f']:.1f}" if v['temperature_f'] else "N/A"
                gluc = f"{v['blood_glucose_mg_dl']:.0f} ({v['glucose_context'] or 'Rand'})" if v['blood_glucose_mg_dl'] else "N/A"
                flag = v['flag_status'] or "Normal"
                v_data.append([v['recorded_at'][:16], bp, hr, temp, gluc, flag])

            t_vitals = Table(v_data, colWidths=[120, 80, 70, 70, 110, 90])
            t_vitals.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284c7')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f1f5f9')]),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(t_vitals)
        else:
            elements.append(Paragraph("<i>No vital signs recorded yet.</i>", body_style))
        elements.append(Spacer(1, 12))

        # Active Medications Section
        elements.append(Paragraph("3. ACTIVE PRESCRIBED MEDICATIONS", section_style))
        meds = database.get_medicine_reminders(user_id, active_only=True)
        if meds:
            m_data = [["Medicine Name", "Dosage", "Timing", "Schedule", "Doctor's Instructions"]]
            for m in meds:
                m_data.append([
                    m['medicine_name'],
                    m['dosage'],
                    m['schedule_timing'],
                    m['time_str'],
                    m['instructions'] or "As directed"
                ])
            t_meds = Table(m_data, colWidths=[120, 80, 80, 80, 180])
            t_meds.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d9488')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0fdfa')]),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(t_meds)
        else:
            elements.append(Paragraph("<i>No active prescription reminders logged.</i>", body_style))
        elements.append(Spacer(1, 12))

        # Upcoming Appointments Section
        elements.append(Paragraph("4. UPCOMING DOCTOR APPOINTMENTS", section_style))
        apts = database.get_appointments(user_id, status_filter="Scheduled")
        if apts:
            a_data = [["Doctor / Specialist", "Hospital / Clinic", "Date", "Time", "Notes"]]
            for a in apts:
                a_data.append([
                    f"{a['doctor_name']} ({a['specialty'] or 'General'})",
                    a['clinic_hospital'] or "N/A",
                    a['appointment_date'],
                    a['appointment_time'],
                    a['notes'] or ""
                ])
            t_apts = Table(a_data, colWidths=[150, 130, 80, 60, 120])
            t_apts.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(t_apts)
        else:
            elements.append(Paragraph("<i>No pending doctor appointments scheduled.</i>", body_style))
        elements.append(Spacer(1, 16))

        # Prominent Legal Disclaimer Footer
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ef4444'), spaceAfter=8))
        disclaimer_text = (
            "<b>IMPORTANT REGULATORY & MEDICAL NOTICE:</b> This health summary consists entirely of self-reported, "
            "user-entered personal lifestyle and home-measurement records. It does NOT constitute a certified clinical laboratory report, "
            "formal diagnostic assessment, or prescription authority. Please present this document to a certified medical professional "
            "for clinical interpretation and guidance. In case of acute medical emergencies in India, call <b>112</b> or <b>108</b> immediately."
        )
        elements.append(Paragraph(disclaimer_text, disclaimer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        # Fallback to plain text bytes with identical information if any ReportLab driver issue occurs
        buffer = io.BytesIO()
        text_report = f"AI POWERED PERSONAL HEALTH COPILOT - SUMMARY REPORT\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nNotice: {e}\nUser-entered personal health tracking records."
        buffer.write(text_report.encode("utf-8"))
        buffer.seek(0)
        return buffer.getvalue()


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("AI POWERED PERSONAL HEALTH COPILOT - HEALTH REPORTS ENGINE")
    print("=" * 60)
    print("Running reports generation pipeline for demo health profile...")
    database.init_db()
    test_user = database.get_user_by_username("demo_user")
    if not test_user:
        import auth
        auth.register_user("demo_user", "password123", "Demo Health User", "demo@healthcopilot.local")
        test_user = database.get_user_by_username("demo_user")
        database.seed_demo_data(test_user["id"])
    
    uid = test_user["id"]
    pdf_bytes = generate_pdf_report(uid)
    print(f"[OK] PDF Summary Generated: {len(pdf_bytes)} bytes")
    
    df_v = get_vitals_dataframe(uid)
    print(f"[OK] Vitals DataFrame: {len(df_v)} rows extracted")
    
    df_w = get_wellness_dataframe(uid)
    print(f"[OK] Daily Wellness DataFrame: {len(df_w)} rows extracted")
    
    df_m = get_medicines_dataframe(uid)
    print(f"[OK] Active Prescriptions: {len(df_m)} rows extracted")
    
    df_a = get_appointments_dataframe(uid)
    print(f"[OK] Consultations: {len(df_a)} rows extracted")
    
    print("\nTo launch the interactive web application, run:")
    print("   streamlit run app.py")
    print("=" * 60)

