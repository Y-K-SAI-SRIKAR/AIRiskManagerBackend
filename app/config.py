import os

from dotenv import load_dotenv


load_dotenv()


# ==========================================================
# Application
# ==========================================================

APP_NAME = os.getenv(
    "APP_NAME",
    "AI Risk Manager Backend",
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)


# ==========================================================
# Database / RDS
# ==========================================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(
    os.getenv(
        "DB_PORT",
        "3306",
    )
)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ==========================================================
# Agent Service
# ==========================================================

AGENT_URL = os.getenv(
    "AGENT_URL",
    "https://airiskmanageragent.onrender.com",
)

AGENT_TIMEOUT = float(
    os.getenv(
        "AGENT_TIMEOUT",
        "120",
    )
)


# ==========================================================
# ML Model Service
# ==========================================================

ML_MODEL_URL = os.getenv(
    "ML_MODEL_URL",
    "https://airiskmanagermlmodel.onrender.com",
)

ML_MODEL_TIMEOUT = float(
    os.getenv(
        "ML_MODEL_TIMEOUT",
        "120",
    )
)


# ==========================================================
# AWS
# ==========================================================

AWS_ACCESS_KEY_ID = os.getenv(
    "AWS_ACCESS_KEY_ID"
)

AWS_SECRET_ACCESS_KEY = os.getenv(
    "AWS_SECRET_ACCESS_KEY"
)

AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-south-1",
)


# ==========================================================
# Backend Input S3 Bucket
# ==========================================================
#
# This bucket stores CSV files uploaded by the frontend.
#
# Single:
#   transactions/{transaction_id}/uploads/transaction.csv
#
# Batch:
#   batches/{batch_id}/uploads/transactions.csv
#
# ==========================================================

S3_INPUT_BUCKET_NAME = os.getenv(
    "S3_INPUT_BUCKET_NAME"
)


# Backward-compatible alias.
#
# If your older code uses S3_BUCKET_NAME, it will continue
# to point to the same Backend input bucket.

S3_BUCKET_NAME = S3_INPUT_BUCKET_NAME


# ==========================================================
# Settings Object
# ==========================================================

class Settings:

    # ------------------------------------------------------
    # Application
    # ------------------------------------------------------

    APP_NAME = APP_NAME
    APP_VERSION = APP_VERSION

    # ------------------------------------------------------
    # Database
    # ------------------------------------------------------

    DB_HOST = DB_HOST
    DB_PORT = DB_PORT
    DB_NAME = DB_NAME
    DB_USER = DB_USER
    DB_PASSWORD = DB_PASSWORD

    # ------------------------------------------------------
    # Agent
    # ------------------------------------------------------

    AGENT_URL = AGENT_URL
    AGENT_TIMEOUT = AGENT_TIMEOUT

    # ------------------------------------------------------
    # ML
    # ------------------------------------------------------

    ML_MODEL_URL = ML_MODEL_URL
    ML_MODEL_TIMEOUT = ML_MODEL_TIMEOUT

    # ------------------------------------------------------
    # AWS
    # ------------------------------------------------------

    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
    AWS_REGION = AWS_REGION

    # ------------------------------------------------------
    # S3
    # ------------------------------------------------------

    S3_INPUT_BUCKET_NAME = S3_INPUT_BUCKET_NAME
    S3_BUCKET_NAME = S3_BUCKET_NAME


settings = Settings()