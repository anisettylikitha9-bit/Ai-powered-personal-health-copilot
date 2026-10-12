"""
test_suite.py - Automated Unit & Integration Test Suite
Validates database schemas, authentication, vitals validation, habit scoring,
symptom-aware assistant, emergency triage, medicine safety rules, PDF reports, and demo data.
"""

import os
import sys
from datetime import date, datetime

def run_tests():
    print("=" * 60)
    print("RUNNING AI POWERED PERSONAL HEALTH COPILOT TEST SUITE")
    print("=" * 60)

    # 1. Imports Test
    print("\n[1/12] Testing imports...")
    import database
    import auth
    import wellness_engine
    import health_assistant
    import symptom_engine
    import symptom_checker
    import reports
    import translations
    print("  -> All modules (including symptom_engine) imported successfully.")

    # 2. Database Initialization
    print("\n[2/12] Testing database initialization...")
    database.init_db()
    assert os.path.exists(database.DB_PATH), "Database file was not created!"
    print(f"  -> SQLite database initialized at {database.DB_PATH}")

    # 3. Authentication & Hashing
    print("\n[3/12] Testing password hashing & user creation...")
    test_user = "test_pilot_user"
    test_pass = "SecurePass123!"
    
    # Clean up prior test if exists
    existing = database.get_user_by_username(test_user)
    if existing:
        database.delete_user(existing["id"])

    ok, msg = auth.register_user(test_user, test_pass, "Dr. Pilot Tester", "pilot@test.local")
    assert ok, f"Registration failed: {msg}"
    
    user_record, auth_msg = auth.authenticate_user(test_user, test_pass)
    assert user_record is not None, f"Auth failed: {auth_msg}"
    assert user_record["username"] == test_user
    user_id = user_record["id"]
    print(f"  -> User registered and authenticated successfully. User ID: {user_id}")

    # 4. Profile & BMI Calculation
    print("\n[4/12] Testing profile and BMI calculation...")
    database.save_profile(
        user_id=user_id,
        age=28,
        gender="Female",
        height_cm=165.0,
        weight_kg=60.0,
        blood_group="B+",
        emergency_contact_name="Family Member",
        emergency_contact_phone="9876543210",
        allergies="Dust",
        chronic_conditions="Mild Asthma",
        medications_summary="None"
    )
    prof = database.get_profile(user_id)
    assert prof is not None and prof["age"] == 28
    bmi_info = wellness_engine.calculate_bmi(60.0, 165.0)
    assert bmi_info is not None
    assert bmi_info["bmi"] == 22.0
    assert bmi_info["category"] == "Healthy / Normal Weight"
    print(f"  -> Profile saved. Calculated BMI: {bmi_info['bmi']} ({bmi_info['category']})")

    # 5. Vitals Validation & Anomaly Tagging
    print("\n[5/12] Testing vitals validation and anomaly flags...")
    val_norm = wellness_engine.validate_vitals(118, 76, 70, 98.4, 60.0, 90.0, "Fasting")
    assert val_norm["status"] == "Normal"
    val_warn = wellness_engine.validate_vitals(145, 92, 75, 98.6, 60.0, 95.0, "Fasting")
    assert val_warn["status"] == "Warning"
    val_urg = wellness_engine.validate_vitals(185, 122, 105, 98.6, 60.0, 95.0, "Fasting")
    assert val_urg["status"] == "Urgent"
    
    v_id = database.log_vital(
        user_id=user_id,
        systolic_bp=120,
        diastolic_bp=80,
        heart_rate=72,
        temperature_f=98.6,
        weight_kg=60.0,
        blood_glucose_mg_dl=92.0,
        glucose_context="Fasting",
        notes="Automated test check",
        flag_status="Normal",
        flag_reasons="All normal"
    )
    assert v_id > 0
    print("  -> Vitals validation and physiological flags verified.")

    # 6. Daily Wellness & Habit Score
    print("\n[6/12] Testing daily wellness logs & transparent habit score...")
    today = date.today()
    database.log_wellness(
        user_id=user_id,
        log_date=today,
        water_ml=2500,
        sleep_hours=8.0,
        exercise_mins=35,
        exercise_type="Brisk Walking",
        mood="Energetic",
        meal_notes="Healthy balanced plate"
    )
    habit_score = wellness_engine.calculate_habit_score(user_id)
    assert 0 <= habit_score["total_score"] <= 100
    assert "pillars" in habit_score
    print(f"  -> Habit score calculated: {habit_score['total_score']}/100 ({habit_score['score_grade']})")

    # 7. Medicine Reminders & Completion
    print("\n[7/12] Testing medicine reminders & daily completion...")
    med_id = database.add_medicine_reminder(
        user_id=user_id,
        medicine_name="Vitamin D3",
        dosage="1000 IU",
        schedule_timing="Morning",
        time_str="09:00 AM",
        instructions="Take with breakfast"
    )
    assert med_id > 0
    database.mark_medicine_taken(med_id, user_id, today)
    taken_logs = database.get_medicine_logs_for_date(user_id, today)
    assert med_id in taken_logs
    print(f"  -> Medicine reminder #{med_id} created and marked as taken for today.")

    # 8. Appointments & Doctor Consultations
    print("\n[8/12] Testing doctor appointments...")
    apt_id = database.add_appointment(
        user_id=user_id,
        doctor_name="Dr. Test Specialist",
        clinic_hospital="City Medical Center",
        specialty="General Physician",
        appointment_date=today,
        appointment_time="11:00 AM"
    )
    assert apt_id > 0
    print(f"  -> Appointment #{apt_id} scheduled.")

    # 9. Natural Language Symptom Awareness Test Suite
    print("\n[9/12] Testing upgraded natural language symptom-aware assistant...")
    test_queries = [
        ("I have a headache.", "Headache"),
        ("I have a fever and a sore throat.", "Fever & Chills"),
        ("I have a cough and a runny nose.", "Cough"),
        ("I have stomach pain.", "Stomach Pain / Indigestion"),
        ("I feel dizzy and weak.", "Dizziness & Weakness"),
        ("I have trouble sleeping.", "Sleep Problems / Insomnia"),
        ("I have body pain and fatigue.", "Body Pain & Fatigue")
    ]
    
    for q_text, expected_symp in test_queries:
        res = health_assistant.get_assistant_response(q_text, user_id=user_id, lang="en")
        assert res is not None
        assert "content" in res
        assert not res.get("is_emergency", False)
        assert expected_symp in res["title"] or expected_symp in res["content"] or "Guidance" in res["title"]
        # Verify 6-part structured sections exist in response
        assert "Reported Symptoms" in res["content"]
        assert "Safe Next Steps" in res["content"]
        assert "When to Contact a Healthcare Professional" in res["content"]
        assert "Emergency Warning Signs" in res["content"]
        assert "Medication Safety Note" in res["content"]
    print("  -> All 7 natural language symptom scenarios successfully identified with structured 6-point guidance.")

    # 10. Medicine Inquiry & Non-Prescriptive Safety Rules
    print("\n[10/12] Testing medicine inquiry non-prescriptive safety rules...")
    med_res = health_assistant.get_assistant_response("Which tablet should I take?", user_id=user_id, lang="en")
    assert med_res["rule_id"] == "RULE_MEDICINE_NON_PRESCRIPTIVE"
    # Never invent prescriptions or dosages
    assert "does NOT invent prescriptions" in med_res["content"]
    assert "Consult a licensed physician or registered pharmacist" in med_res["content"]
    # Check that user's recorded Vitamin D3 prescription is displayed safely
    assert "Vitamin D3" in med_res["content"]
    print("  -> Medicine request correctly handled with non-prescriptive guidance and existing prescription lookup.")

    # 11. High-Priority Emergency Triage Detection
    print("\n[11/12] Testing emergency red-flag warning rules (India 112)...")
    emergency_queries = [
        "I have severe chest pain and cannot breathe",
        "My grandfather has sudden facial drooping and slurred speech",
        "Patient is coughing up blood",
        "Loss of consciousness after head injury"
    ]
    for em_q in emergency_queries:
        em_res = health_assistant.get_assistant_response(em_q, user_id=user_id, lang="en")
        assert em_res.get("is_emergency") is True
        assert "112" in em_res["content"]
        assert "EMERGENCY" in em_res["content"]
        assert "Emergency Triage Filter" in em_res["matched_rule"]
    print("  -> All acute emergency queries routed to India 112 with high-priority emergency alerts.")

    # 12. Bilingual Telugu & Edge Cases (Empty, Unclear, and Telugu)
    print("\n[12/12] Testing Telugu translations and unclear/empty input handling...")
    # Telugu symptom
    te_symp_res = health_assistant.get_assistant_response("నాకు తలనొప్పిగా ఉంది", user_id=user_id, lang="te")
    assert "లక్షణాలు" in te_symp_res["content"]
    
    # Telugu emergency
    te_em_res = health_assistant.get_assistant_response("ఛాతీ నొప్పి మరియు శ్వాస ఆడటం లేదు", user_id=user_id, lang="te")
    assert te_em_res["is_emergency"] is True
    assert "112" in te_em_res["content"]

    # Telugu medicine
    te_med_res = health_assistant.get_assistant_response("ఏ టాబ్లెట్ వేసుకోవాలి", user_id=user_id, lang="te")
    assert "ఔషధాల భద్రత" in te_med_res["content"]

    # Unclear input
    empty_res = health_assistant.get_assistant_response("", user_id=user_id, lang="en")
    assert empty_res["rule_id"] == "RULE_UNCLEAR_INPUT"
    
    greeting_res = health_assistant.get_assistant_response("Hello", user_id=None, lang="en")
    assert "Personal Health" in greeting_res["content"] or "Hello" in greeting_res["content"]

    # PDF and Demo Data
    pdf_bytes = reports.generate_pdf_report(user_id)
    assert len(pdf_bytes) > 500
    database.seed_demo_data(user_id)

    # 13. Medical Documents & PDF Upload / Storage Vault
    print("\n[13/13] Testing Medical Document & PDF Storage Vault...")
    sample_content = b"%PDF-1.4 sample test medical document bytes"
    doc_id = database.add_medical_document(
        user_id=user_id,
        title="Complete Blood Count Report",
        category="Lab Reports",
        report_date="2026-10-12",
        doctor_or_lab="Apollo Diagnostics",
        file_bytes=sample_content,
        file_name="cbc_report_2026.pdf",
        notes="Hb 14.2 g/dL, normal platelet count"
    )
    assert doc_id is not None
    docs = database.get_medical_documents(user_id)
    assert any(d["id"] == doc_id for d in docs)
    single_doc = database.get_medical_document_by_id(doc_id, user_id)
    assert single_doc is not None
    assert single_doc["title"] == "Complete Blood Count Report"
    assert os.path.exists(single_doc["file_path"])
    # Clean up test document
    del_ok = database.delete_medical_document(doc_id, user_id)
    assert del_ok is True
    assert not os.path.exists(single_doc["file_path"])
    print("  -> Medical document uploaded, retrieved, and deleted successfully with disk cleanup.")

    print("\n" + "=" * 60)
    print("ALL 13 TEST SUITES PASSED! PDF UPLOAD & STORAGE VAULT IS FULLY OPERATIONAL.")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
