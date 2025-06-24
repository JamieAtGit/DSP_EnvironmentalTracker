"""
Secure CORS Configuration
========================

Replace the overly permissive CORS configuration with this secure version.
"""

from flask_cors import CORS
import os

def configure_secure_cors(app):
    """Configure CORS with security best practices"""
    
    # Get allowed origins from environment
    allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # Remove any empty strings and whitespace
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    
    # Configure CORS with restricted origins
    CORS(app, 
         origins=allowed_origins,  # Specific origins only
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         max_age=86400  # Cache preflight for 24 hours
    )
    
    return app

# Example usage in app.py:
# from config.cors_security import configure_secure_cors
# app = configure_secure_cors(app)
