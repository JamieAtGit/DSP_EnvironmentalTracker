"""
Security utilities and middleware for the Carbon Footprint Tracking System.
"""
import functools
import re
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from flask import request, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure security logging
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

class SecurityError(Exception):
    """Base class for security-related errors."""
    pass

class RateLimitExceeded(SecurityError):
    """Raised when rate limit is exceeded."""
    pass

class ValidationError(SecurityError):
    """Raised when input validation fails."""
    pass

# In-memory rate limiting (use Redis in production)
rate_limit_storage = defaultdict(lambda: deque())

def rate_limit(requests_per_minute=60, requests_per_hour=1000):
    """
    Rate limiting decorator.
    
    Args:
        requests_per_minute: Maximum requests per minute per IP
        requests_per_hour: Maximum requests per hour per IP
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = get_client_ip()
            current_time = time.time()
            
            # Clean old entries
            minute_ago = current_time - 60
            hour_ago = current_time - 3600
            
            # Get request history for this IP
            ip_requests = rate_limit_storage[client_ip]
            
            # Remove old requests
            while ip_requests and ip_requests[0] < hour_ago:
                ip_requests.popleft()
            
            # Count recent requests
            recent_minute = sum(1 for req_time in ip_requests if req_time > minute_ago)
            recent_hour = len(ip_requests)
            
            # Check limits
            if recent_minute >= requests_per_minute:
                security_logger.warning(f"Rate limit exceeded (minute) for IP: {client_ip}")
                return jsonify({
                    "error": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                }), 429
            
            if recent_hour >= requests_per_hour:
                security_logger.warning(f"Rate limit exceeded (hour) for IP: {client_ip}")
                return jsonify({
                    "error": "Rate limit exceeded. Please try again in an hour.",
                    "retry_after": 3600
                }), 429
            
            # Record this request
            ip_requests.append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_auth(roles=None):
    """
    Authentication decorator.
    
    Args:
        roles: List of required roles (optional)
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user = session.get('user')
            if not user:
                security_logger.warning(f"Unauthorized access attempt to {request.endpoint} from {get_client_ip()}")
                return jsonify({"error": "Authentication required"}), 401
            
            if roles and user.get('role') not in roles:
                security_logger.warning(f"Insufficient privileges for {user.get('username')} accessing {request.endpoint}")
                return jsonify({"error": "Insufficient privileges"}), 403
            
            # Store user in g for easy access in view functions
            g.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_input(schema):
    """
    Input validation decorator.
    
    Args:
        schema: Dictionary defining validation rules
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON payload"}), 400
            
            errors = []
            
            for field, rules in schema.items():
                value = data.get(field)
                
                # Check required fields
                if rules.get('required', False) and value is None:
                    errors.append(f"Field '{field}' is required")
                    continue
                
                if value is not None:
                    # Type validation
                    expected_type = rules.get('type')
                    if expected_type and not isinstance(value, expected_type):
                        errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
                        continue
                    
                    # String validations
                    if isinstance(value, str):
                        min_len = rules.get('min_length')
                        max_len = rules.get('max_length')
                        pattern = rules.get('pattern')
                        
                        if min_len and len(value) < min_len:
                            errors.append(f"Field '{field}' must be at least {min_len} characters")
                        if max_len and len(value) > max_len:
                            errors.append(f"Field '{field}' must be at most {max_len} characters")
                        if pattern and not re.match(pattern, value):
                            errors.append(f"Field '{field}' has invalid format")
                    
                    # Numeric validations
                    if isinstance(value, (int, float)):
                        min_val = rules.get('min_value')
                        max_val = rules.get('max_value')
                        
                        if min_val is not None and value < min_val:
                            errors.append(f"Field '{field}' must be at least {min_val}")
                        if max_val is not None and value > max_val:
                            errors.append(f"Field '{field}' must be at most {max_val}")
                    
                    # Choice validation
                    choices = rules.get('choices')
                    if choices and value not in choices:
                        errors.append(f"Field '{field}' must be one of: {', '.join(map(str, choices))}")
            
            if errors:
                security_logger.warning(f"Validation errors from {get_client_ip()}: {errors}")
                return jsonify({"error": "Validation failed", "details": errors}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_output(data):
    """
    Sanitize output data to prevent information disclosure.
    """
    if isinstance(data, dict):
        # Remove sensitive keys
        sensitive_keys = ['password', 'secret', 'token', 'key', 'hash']
        return {k: sanitize_output(v) for k, v in data.items() 
                if not any(sensitive in k.lower() for sensitive in sensitive_keys)}
    elif isinstance(data, list):
        return [sanitize_output(item) for item in data]
    else:
        return data

def get_client_ip():
    """Get real client IP address."""
    # Check for forwarded IP (behind proxy)
    if request.headers.get('X-Forwarded-For'):
        # Take the first IP in the chain
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def secure_headers(response):
    """Add security headers to response."""
    from backend.config import Config
    
    for header, value in Config.SECURITY_HEADERS.items():
        response.headers[header] = value
    
    return response

def log_security_event(event_type, details, severity='INFO'):
    """Log security events for monitoring."""
    security_logger.log(
        getattr(logging, severity),
        f"SECURITY_EVENT: {event_type} | IP: {get_client_ip()} | "
        f"User: {session.get('user', {}).get('username', 'anonymous')} | "
        f"Details: {details} | Time: {datetime.utcnow().isoformat()}"
    )

def safe_error_response(error, status_code=500):
    """
    Return safe error response that doesn't expose internal details.
    """
    # Log the actual error for debugging
    security_logger.error(f"Internal error: {str(error)} | IP: {get_client_ip()}")
    
    # Return generic error to client
    safe_errors = {
        400: "Bad request",
        401: "Authentication required", 
        403: "Access forbidden",
        404: "Resource not found",
        429: "Rate limit exceeded",
        500: "Internal server error"
    }
    
    return jsonify({
        "error": safe_errors.get(status_code, "An error occurred"),
        "status": status_code
    }), status_code

# Common validation schemas
PREDICTION_SCHEMA = {
    'material': {
        'required': False,
        'type': str,
        'max_length': 50,
        'choices': ['Plastic', 'Glass', 'Metal', 'Wood', 'Paper', 'Cardboard', 'Other']
    },
    'weight': {
        'required': False,
        'type': (int, float),
        'min_value': 0,
        'max_value': 1000  # kg
    },
    'origin': {
        'required': False,
        'type': str,
        'max_length': 100
    },
    'transport': {
        'required': False,
        'type': str,
        'choices': ['Air', 'Ship', 'Truck', 'Rail', 'Land']
    },
    'recyclability': {
        'required': False,
        'type': str,
        'choices': ['High', 'Medium', 'Low']
    }
}

AUTH_SCHEMA = {
    'username': {
        'required': True,
        'type': str,
        'min_length': 3,
        'max_length': 50,
        'pattern': r'^[a-zA-Z0-9_]+$'  # Alphanumeric and underscore only
    },
    'password': {
        'required': True,
        'type': str,
        'min_length': 8,
        'max_length': 128
    }
}