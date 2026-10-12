"""
backend/app/auth.py - Authentication & Security Engine
Secure PBKDF2-HMAC-SHA256 password hashing with unique salts.
Supports token generation, user registration, and authentication via SQLAlchemy.
"""

import hashlib
import secrets
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
try:
    from backend.app.models import User, Profile, WellnessGoal
except ImportError:
    from .models import User, Profile, WellnessGoal


HASH_ITERATIONS = 100_000


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


def register_user(
    db: Session,
    username: str,
    password: str,
    full_name: str,
    email: Optional[str] = ""
) -> Tuple[bool, str, Optional[User]]:
    """Registers a new user into the database using SQLAlchemy with parameterized safety."""
    username = username.strip().lower()
    full_name = full_name.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters long.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    if not full_name:
        return False, "Please enter your full name.", None

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return False, "Username is already registered. Please choose another.", None

    pwd_hash, salt = hash_password(password)
    user = User(
        username=username,
        password_hash=pwd_hash,
        salt=salt,
        full_name=full_name,
        email=email or ""
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize default profile and wellness goals
    profile = Profile(user_id=user.id, age=30, gender="Not Specified")
    goal = WellnessGoal(user_id=user.id)
    db.add(profile)
    db.add(goal)
    db.commit()

    return True, "Registration successful.", user


def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> Tuple[Optional[Dict[str, Any]], str]:
    """Authenticates username and password against database."""
    username = username.strip().lower()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None, "Invalid username or password."

    if not verify_password(password, user.password_hash, user.salt):
        return None, "Invalid username or password."

    # Return safe user dictionary without sensitive hash/salt
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "token": secrets.token_urlsafe(32)  # session auth token
    }, "Authentication successful."
