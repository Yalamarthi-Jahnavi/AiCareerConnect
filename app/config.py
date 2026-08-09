"""
AI Career Connect - Configuration
===================================
Holds all configuration classes for different environments.

WHY THIS FILE EXISTS:
    Centralizes ALL configuration in one place. Separate classes for
    development, testing, and production prevent accidental use of
    debug settings in production. Environment variables keep secrets
    out of source code.
"""

import os
from datetime import timedelta

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class BaseConfig:
    """Base configuration shared across all environments."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-career-connect-secret-key-change-in-production')
    
    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "instance", "ai_career_connect.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Mistral AI API Configuration
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', '')
    MISTRAL_MODEL = os.environ.get('MISTRAL_MODEL', 'mistral-large-latest')
    MISTRAL_API_URL = 'https://api.mistral.ai/v1/chat/completions'
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    # Speech Configuration
    SPEECH_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'audio')
    TTS_OUTPUT_FOLDER = os.path.join(BASE_DIR, 'static', 'audio')


class DevelopmentConfig(BaseConfig):
    """Development configuration - debug mode ON, verbose logging."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log all SQL queries


class TestingConfig(BaseConfig):
    """Testing configuration - uses in-memory SQLite for speed."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(BaseConfig):
    """Production configuration - debug OFF, strict security."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


# Dictionary to easily select config by name
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
