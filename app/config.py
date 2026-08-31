import os

from dotenv import load_dotenv


load_dotenv()


APP_NAME = os.getenv(
    "APP_NAME",
    "AI Risk Manager Backend"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)

DEBUG = os.getenv(
    "DEBUG",
    "false"
).lower() == "true"

PORT = int(
    os.getenv(
        "PORT",
        "8002"
    )
)


# =========================
# Database
# =========================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# =========================
# External Services
# =========================

ML_MODEL_URL = os.getenv(
    "ML_MODEL_URL",
    "https://airiskmanagermlmodel.onrender.com"
).rstrip("/")


AGENT_URL = os.getenv(
    "AGENT_URL",
    "https://airiskmanageragent.onrender.com"
).rstrip("/")


# =========================
# Validation
# =========================

required_settings = {
    "DB_HOST": DB_HOST,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}


missing_settings = [
    key
    for key, value in required_settings.items()
    if not value
]


if missing_settings:
    raise ValueError(
        "Missing required environment variables: "
        + ", ".join(missing_settings)
    )