"""
Application configuration for AI Career Connect.

Contains configuration classes for development, testing, and production.
Environment variables are used for secrets and deployment-specific settings.
"""

import os
from datetime import timedelta


# ============================================================
# Base Configuration
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)


class BaseConfig:
    """Configuration shared across all environments."""

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "ai-career-connect-secret-key-change-in-production"
    )

    # ========================================================
    # Database
    # ========================================================

    # Render can provide DATABASE_URL.
    # Otherwise, use a writable temporary SQLite database.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:////tmp/ai_career_connect.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ========================================================
    # JWT
    # ========================================================

    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY",
        "jwt-secret-key-change-in-production"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # ========================================================
    # Mistral AI
    # ========================================================

    MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")

    MISTRAL_MODEL = os.environ.get(
        "MISTRAL_MODEL",
        "mistral-large-latest"
    )

    MISTRAL_API_URL = (
        "https://api.mistral.ai/v1/chat/completions"
    )

    # ========================================================
    # File Uploads
    # ========================================================

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "txt"
    }

    # ========================================================
    # Speech
    # ========================================================

    SPEECH_UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads",
        "audio"
    )

    TTS_OUTPUT_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "audio"
    )


# ============================================================
# Development Configuration
# ============================================================

class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True


# ============================================================
# Testing Configuration
# ============================================================

class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


# ============================================================
# Production Configuration
# ============================================================

class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_ECHO = False


# ============================================================
# Configuration Mapping
# ============================================================

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}