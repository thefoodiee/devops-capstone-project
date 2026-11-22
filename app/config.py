import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database configuration
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "notes_db")
    
    # Priority: explicit DATABASE_URL, then Postgres composite, then SQLite fallback
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
        elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif os.getenv("USE_SQLITE", "false").lower() == "true":
        SQLALCHEMY_DATABASE_URI = "sqlite:///notes.db"
    else:
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
