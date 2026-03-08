"""
Minimal Django settings to run care_im with WhatsApp for demo/video.
Usage: python manage_demo.py runserver
Loads .env from project root if python-dotenv is installed; else set env vars.
"""
import os

# Load .env from repo root when running demo (optional)
try:
    from pathlib import Path
    from dotenv import load_dotenv
    repo_root = Path(__file__).resolve().parent.parent
    load_dotenv(repo_root / ".env")
except ImportError:
    pass

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "demo-secret-change-in-production")
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "care_im",
]

BASE_DIR = Path(__file__).resolve().parent

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

ROOT_URLCONF = "demo_site.urls"

IM_BACKEND = "care_im.backends.whatsapp.WhatsAppBackend"
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "care_im_demo_2025")

# Optional: custom reply for demo (default is echo)
# CARE_IM_WHATSAPP_DEMO_REPLY = "Thanks! CARE IM bot received your message."

# Show webhook logs in console when running runserver
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "care_im": {"level": "INFO", "handlers": ["console"]},
    },
}
