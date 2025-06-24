"""
Security Middleware for Advanced Eco-Score Prediction System
===========================================================

Implements security headers and request validation.
"""

from flask import request, Response
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Comprehensive security middleware"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        app.after_request(self.add_security_headers)
        app.before_request(self.validate_request)
    
    def add_security_headers(self, response: Response) -> Response:
        """Add comprehensive security headers"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
            
        return response
    
    def validate_request(self):
        """Validate incoming requests for security issues"""
        # Block requests with suspicious user agents
        user_agent = request.headers.get('User-Agent', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'dirb', 'nmap']
        
        if any(agent in user_agent for agent in suspicious_agents):
            logger.warning(f"Blocked suspicious user agent: {user_agent}")
            return "Forbidden", 403
        
        # Validate content length
        if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
            logger.warning(f"Request too large: {request.content_length} bytes")
            return "Request too large", 413
        
        # Block common attack patterns in URLs
        suspicious_patterns = ['../', '..\\', '<script', 'javascript:', 'vbscript:']
        url = request.url.lower()
        
        if any(pattern in url for pattern in suspicious_patterns):
            logger.warning(f"Blocked suspicious URL pattern: {request.url}")
            return "Forbidden", 403

def require_https(f):
    """Decorator to require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not current_app.debug:
            return redirect(request.url.replace('http://', 'https://'))
        return f(*args, **kwargs)
    return decorated_function

def validate_json_request(f):
    """Decorator to validate JSON requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json:
            try:
                # Validate JSON structure
                data = request.get_json()
                if data is None:
                    return {"error": "Invalid JSON"}, 400
            except Exception:
                return {"error": "Invalid JSON format"}, 400
        return f(*args, **kwargs)
    return decorated_function
