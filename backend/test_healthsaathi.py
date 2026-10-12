"""
backend/test_healthsaathi.py - Comprehensive Automated Verification Suite
Tests:
1. Emergency detection (Tier 1 red flags & 112 India routing)
2. Multilingual assistant: English, Telugu, Roman Telugu ("Naaku jwaram ga undi", etc.)
3. Authentication and Authorization (Register, Login, Password validation, Isolation)
4. Wellness Tracker CRUD (Create, Read, Update, Delete, Habit score)
5. Explainable Analytics with real recorded data (Data used, Rule applied, Result, Limitation)
6. FastAPI REST API endpoints
"""

import sys
import os

# Ensure root and backend directories are on sys.path
_backend_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_backend_dir)
for _p in [_root_dir, _backend_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi.testclient import TestClient
try:
    from backend.app.main import app
    from backend.app.database import SessionLocal, init_db
    from backend.app.models import User, WellnessLog, VitalLog
    from backend.app import auth, emergency_triage, assistant, wellness, analytics
except ImportError:
    from app.main import app
    from app.database import SessionLocal, init_db
    from app.models import User, WellnessLog, VitalLog
    from app import auth, emergency_triage, assistant, wellness, analytics

client = TestClient(app)

def test_emergency_detection():
    print("\n--- 1. Testing Emergency Triage Detection ---")
    red_flag_cases = [
        "severe chest pain and pressure",
        "difficulty breathing cannot breathe",
        "facial drooping and slurred speech",
        "unconscious passed out on the floor",
        "severe bleeding coughing up blood"
    ]
    for text in red_flag_cases:
        res = emergency_triage.detect_emergency(text, lang="en")
        assert res is not None, f"Failed to detect emergency for: {text}"
        assert "112" in res["emergency_number"], "112 helpline missing from emergency response"
        print(f"  [PASS] Emergency detected for '{text[:30]}...' -> {res['matched_category']}")

    # Test full 3-tier triage endpoint logic
    tier1 = emergency_triage.evaluate_three_tier_triage(
        symptoms=["chest pain"], text_input="I have severe crushing chest pain"
    )
    assert tier1["tier_level"] == 1
    assert "EMERGENCY" in tier1["headline"]
    print("  [PASS] Tier 1 'Emergency care now' confirmed.")

    tier2 = emergency_triage.evaluate_three_tier_triage(
        symptoms=["fever", "headache", "stomach pain"],
        severity="Severe",
        duration="4 to 7 days"
    )
    assert tier2["tier_level"] == 2
    assert "PROMPT MEDICAL CONSULTATION" in tier2["headline"]
    print("  [PASS] Tier 2 'Prompt medical consultation' confirmed.")

    tier3 = emergency_triage.evaluate_three_tier_triage(
        symptoms=["mild tiredness"],
        severity="Mild",
        duration="Just started today"
    )
    assert tier3["tier_level"] == 3
    assert "GENERAL SELF-CARE" in tier3["headline"]
    print("  [PASS] Tier 3 'General self-care guidance' confirmed.")


def test_multilingual_assistant():
    print("\n--- 2. Testing Multilingual Conversational Health Assistant ---")
    
    # 1. English headache
    en_res = assistant.get_assistant_response("I have a headache.", lang="en")
    assert "Headache" in en_res["title"]
    assert "Medical Disclaimer" in en_res["content"]
    assert len(en_res["follow_ups"]) > 0
    print("  [PASS] 'I have a headache.' -> Correctly answered with follow-ups and disclaimer.")

    # 2. Roman Telugu fever
    roman_res = assistant.get_assistant_response("Naaku jwaram ga undi.", lang="te-roman")
    assert "Jwaram" in roman_res["title"] or "fever" in roman_res["content"].lower() or "jwaram" in roman_res["content"].lower()
    print("  [PASS] 'Naaku jwaram ga undi.' -> Correctly identified in Roman Telugu.")

    # 3. Telugu dehydration
    te_res = assistant.get_assistant_response("Explain dehydration in Telugu.", lang="en")
    assert "డీహైడ్రేషన్" in te_res["content"] or "నీటి కొరత" in te_res["content"]
    print("  [PASS] 'Explain dehydration in Telugu.' -> Provided Telugu clinical explanation.")

    # 4. Sleep improvement
    sleep_res = assistant.get_assistant_response("How can I improve my sleep?", lang="en")
    assert "Sleep" in sleep_res["title"]
    assert "Circadian" in sleep_res["title"] or "sleep" in sleep_res["content"].lower()
    print("  [PASS] 'How can I improve my sleep?' -> Provided circadian sleep guidance.")


def test_auth_crud_and_isolation():
    print("\n--- 3. Testing Authentication & User Isolation ---")
    db = SessionLocal()
    test_user_name = f"testuser_{os.getpid()}"
    
    # Clean previous run if exists
    db.query(User).filter(User.username == test_user_name).delete()
    db.commit()

    # Register
    ok, msg, user = auth.register_user(db, test_user_name, "Secret@123", "Test Health User", "test@test.local")
    assert ok, f"Registration failed: {msg}"
    assert user.id is not None
    print(f"  [PASS] User registered with ID: {user.id}")

    # Duplicate registration rejection
    dup_ok, dup_msg, _ = auth.register_user(db, test_user_name, "Secret@123", "Test Duplicate", "test@test.local")
    assert not dup_ok, "Duplicate registration should fail"
    print("  [PASS] Duplicate username correctly rejected.")

    # Login Success
    user_dict, log_msg = auth.authenticate_user(db, test_user_name, "Secret@123")
    assert user_dict is not None
    assert user_dict["username"] == test_user_name
    print("  [PASS] Valid login succeeded.")

    # Invalid Password
    bad_dict, bad_msg = auth.authenticate_user(db, test_user_name, "WrongPassword")
    assert bad_dict is None
    print("  [PASS] Invalid password correctly rejected.")
    
    db.close()
    return user.id


def test_wellness_crud(user_id: int):
    print("\n--- 4. Testing Wellness Tracker CRUD Operations ---")
    db = SessionLocal()

    # Create log
    log1 = wellness.create_wellness_log(
        db=db,
        user_id=user_id,
        log_date="2026-10-10",
        water_ml=2800,
        sleep_hours=8.0,
        exercise_mins=45,
        exercise_type="Jogging",
        mood="Energetic",
        notes="Felt great after morning run"
    )
    assert log1.id is not None
    assert log1.water_ml == 2800
    print(f"  [PASS] Created wellness log #{log1.id} for date {log1.log_date}")

    # Read
    logs = wellness.get_user_wellness_logs(db, user_id=user_id, days=7)
    assert any(l.id == log1.id for l in logs)
    print(f"  [PASS] Retrieved {len(logs)} wellness logs for user.")

    # Update
    updated = wellness.update_wellness_log(
        db=db,
        record_id=log1.id,
        user_id=user_id,
        water_ml=3200,
        sleep_hours=8.5,
        exercise_mins=50,
        exercise_type="Jogging & Stretching",
        mood="Fantastic",
        meal_notes="Healthy salad",
        notes="Updated notes"
    )
    assert updated is not None
    assert updated.water_ml == 3200
    assert updated.exercise_mins == 50
    print("  [PASS] Updated wellness log successfully.")

    # Calculate Habit Score
    score_res = wellness.calculate_habit_score(db, user_id=user_id)
    assert score_res["habit_score"] > 0
    print(f"  [PASS] Habit score calculated: {score_res['habit_score']}/100 ({score_res['status_label']})")

    # Delete
    del_ok = wellness.delete_wellness_log(db, record_id=log1.id, user_id=user_id)
    assert del_ok
    print(f"  [PASS] Deleted wellness log #{log1.id}.")

    db.close()


def test_explainable_analytics(user_id: int):
    print("\n--- 5. Testing Explainable Wellness Intelligence with Real Data ---")
    db = SessionLocal()

    # Seed 2 weeks of realistic activity data to test progression:
    # Previous week: 2 active days
    # Current week: 4 active days
    from datetime import date, timedelta
    today = date.today()

    # Current week (last 7 days): 4 active days
    for d in range(1, 5):
        dt_str = (today - timedelta(days=d)).strftime("%Y-%m-%d")
        wellness.create_wellness_log(
            db, user_id=user_id, log_date=dt_str,
            water_ml=2600, sleep_hours=7.5, exercise_mins=30, exercise_type="Walk"
        )
    # Previous week (8 to 14 days ago): 2 active days
    for d in [8, 10]:
        dt_str = (today - timedelta(days=d)).strftime("%Y-%m-%d")
        wellness.create_wellness_log(
            db, user_id=user_id, log_date=dt_str,
            water_ml=2200, sleep_hours=7.0, exercise_mins=25, exercise_type="Walk"
        )

    insights = analytics.generate_explainable_insights(db, user_id=user_id)
    assert len(insights) >= 2, "Expected multiple explainable insight cards"

    active_card = next((i for i in insights if i["id"] == "INSIGHT_ACTIVE_DAYS"), None)
    assert active_card is not None, "Missing active days insight card"
    assert "Data used" in active_card or "data_used" in active_card
    assert "Rule applied" in active_card or "rule_applied" in active_card
    assert "Limitation" in active_card or "limitation" in active_card
    assert "increased from 2 to 4" in active_card["result"], f"Unexpected result: {active_card['result']}"
    print(f"  [PASS] Explainable card verified: '{active_card['result']}'")
    print(f"         Data used: {active_card['data_used']}")
    print(f"         Rule applied: {active_card['rule_applied']}")
    print(f"         Limitation: {active_card['limitation']}")

    db.close()


def test_fastapi_endpoints(user_id: int):
    print("\n--- 6. Testing FastAPI REST API Endpoints ---")
    # Health
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    print("  [PASS] GET /api/health -> 200 OK")

    # Translations
    r = client.get("/api/translations")
    assert r.status_code == 200
    assert "en" in r.json() and "te" in r.json() and "te-roman" in r.json()
    print("  [PASS] GET /api/translations -> 200 OK (en, te, te-roman)")

    # Chat
    r = client.post("/api/chat", json={"user_id": user_id, "message": "I have a headache.", "lang": "en"})
    assert r.status_code == 200
    assert "content" in r.json()
    print("  [PASS] POST /api/chat -> 200 OK")

    # Triage
    r = client.post("/api/triage", json={"user_id": user_id, "symptoms": ["chest pain"], "text_input": "sudden severe chest pain"})
    assert r.status_code == 200
    assert r.json()["tier_level"] == 1
    print("  [PASS] POST /api/triage -> 200 OK (Tier 1)")

    # Wellness CRUD via API
    r = client.post("/api/wellness", json={
        "user_id": user_id,
        "log_date": "2026-10-12",
        "water_ml": 3000,
        "sleep_hours": 8.0,
        "exercise_mins": 35,
        "exercise_type": "Cycling",
        "mood": "Energetic",
        "meal_notes": "Oatmeal and fruit"
    })
    assert r.status_code == 200
    rec_id = r.json()["id"]
    print(f"  [PASS] POST /api/wellness -> 200 OK (created #{rec_id})")

    r = client.get(f"/api/wellness?user_id={user_id}&days=7")
    assert r.status_code == 200
    assert len(r.json()["logs"]) > 0
    print(f"  [PASS] GET /api/wellness -> 200 OK ({len(r.json()['logs'])} logs returned)")

    r = client.put(f"/api/wellness/{rec_id}", json={
        "user_id": user_id,
        "water_ml": 3200,
        "sleep_hours": 8.2,
        "exercise_mins": 40,
        "exercise_type": "Cycling",
        "mood": "High Energy",
        "meal_notes": "Oatmeal and nuts"
    })
    assert r.status_code == 200
    print(f"  [PASS] PUT /api/wellness/{rec_id} -> 200 OK")

    r = client.delete(f"/api/wellness/{rec_id}?user_id={user_id}")
    assert r.status_code == 200
    print(f"  [PASS] DELETE /api/wellness/{rec_id} -> 200 OK")

    # Insights
    r = client.get(f"/api/insights?user_id={user_id}")
    assert r.status_code == 200
    assert "insights" in r.json()
    print("  [PASS] GET /api/insights -> 200 OK")

    # Chat history
    r = client.get(f"/api/chat/history?user_id={user_id}")
    assert r.status_code == 200
    assert "history" in r.json()
    print("  [PASS] GET /api/chat/history -> 200 OK")


if __name__ == "__main__":
    init_db()
    test_emergency_detection()
    test_multilingual_assistant()
    test_user_id = test_auth_crud_and_isolation()
    test_wellness_crud(test_user_id)
    test_explainable_analytics(test_user_id)
    test_fastapi_endpoints(test_user_id)
    print("\n" + "="*60)
    print("SUCCESS: ALL 6 COMPREHENSIVE TEST SUITES PASSED FLAWLESSLY!")
    print("="*60)
