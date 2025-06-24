"""
Production Configuration for Advanced Eco-Score Prediction System
================================================================

CRITICAL: Review all settings before production deployment!
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration with security hardening"""
    
    # Security Settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set!")
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable must be set!")
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'postgresql://eco_user:secure_password@localhost/eco_score_prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {'sslmode': 'require'}  # Require SSL
    }
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    # Session Security
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    CORS_ALLOW_CREDENTIALS = True
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # File Upload Security
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx'}
    UPLOAD_FOLDER = '/secure/uploads'
    
    # ML Configuration
    MODEL_PATH = os.environ.get('MODEL_PATH', '/secure/models/')
    ENABLE_MODEL_MONITORING = True
    ENABLE_DRIFT_DETECTION = True
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
    
    # Email Configuration (for alerts)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Monitoring
    ENABLE_PROMETHEUS_METRICS = True
    HEALTH_CHECK_TIMEOUT = 30
    
    # Development flags
    DEBUG = False
    TESTING = False
