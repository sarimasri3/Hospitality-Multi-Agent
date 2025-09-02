"""
Configuration settings for the Hospitality Booking System.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Google Cloud / Firebase
FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID", "hospitality-booking-dev")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ADK Configuration
ADK_MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Session Configuration
SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "30"))
STM_MAX_SIZE_MB = int(os.getenv("STM_MAX_SIZE_MB", "100"))

# Feature Flags
ENABLE_UPSELL = os.getenv("ENABLE_UPSELL", "true").lower() == "true"
ENABLE_SURVEY = os.getenv("ENABLE_SURVEY", "true").lower() == "true"
ENABLE_PRECHECKIN = os.getenv("ENABLE_PRECHECKIN", "true").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", str(LOGS_DIR / "hospitality.log"))

# Business Rules
MIN_BOOKING_DAYS = 1  # Minimum nights for a booking
MAX_BOOKING_DAYS = 30  # Maximum nights for a booking
MAX_GUESTS_PER_BOOKING = 10
BOOKING_ADVANCE_DAYS = 365  # How far in advance bookings can be made

# Pricing Configuration
BASE_CLEANING_FEE = 50.0
SERVICE_FEE_PERCENTAGE = 0.1  # 10% service fee
TAX_PERCENTAGE = 0.08  # 8% tax

# Upsell Packages
UPSELL_PACKAGES = {
    "early_checkin": {"name": "Early Check-in", "price": 50.0, "description": "Check in at 12 PM"},
    "late_checkout": {"name": "Late Check-out", "price": 50.0, "description": "Check out at 2 PM"},
    "welcome_basket": {"name": "Welcome Basket", "price": 75.0, "description": "Local treats and wine"},
    "spa_package": {"name": "Spa Package", "price": 200.0, "description": "In-villa spa treatment"},
    "chef_service": {"name": "Private Chef", "price": 300.0, "description": "Personal chef for dinner"},
}

# Survey Configuration
SURVEY_DELAY_HOURS = 24  # Hours after checkout to send survey
SURVEY_REMINDER_HOURS = 72  # Send reminder if not completed

# Pre-checkin Configuration
PRECHECKIN_REMINDER_HOURS = 48  # Hours before check-in to send reminder