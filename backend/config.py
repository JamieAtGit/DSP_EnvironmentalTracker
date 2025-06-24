import os
import secrets
from datetime import timedelta
####

class Config:
    """Base configuration with secure defaults."""
    
    # Generate a secure secret key if not provided
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # Generate a cryptographically secure random secret key
        SECRET_KEY = secrets.token_urlsafe(32)
        print("⚠️  WARNING: Using generated secret key. Set SECRET_KEY environment variable for production!")
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # Only send over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JS access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///carbon_tracker.db')
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # Rate limiting
    RATE_LIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
    
    # File upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    CORS_ORIGINS = ['*']  # Allow all origins in development

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Force HTTPS in production
    PREFERRED_URL_SCHEME = 'https'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration selection
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}