"""
Authentication Security Enhancements
===================================

Additional security measures for authentication.
"""

from functools import wraps
from flask import request, session, jsonify, current_app
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Track failed login attempts
failed_attempts = defaultdict(list)
blocked_ips = defaultdict(float)

def rate_limit_auth(max_attempts=5, block_duration=300):
    """Rate limiting decorator for authentication endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = time.time()
            
            # Check if IP is currently blocked
            if client_ip in blocked_ips and current_time < blocked_ips[client_ip]:
                remaining = int(blocked_ips[client_ip] - current_time)
                return jsonify({
                    'error': f'Too many failed attempts. Try again in {remaining} seconds.'
                }), 429
            
            # Clean up old attempts
            if client_ip in failed_attempts:
                failed_attempts[client_ip] = [
                    attempt for attempt in failed_attempts[client_ip]
                    if current_time - attempt < block_duration
                ]
            
            # Check attempt count
            if len(failed_attempts[client_ip]) >= max_attempts:
                blocked_ips[client_ip] = current_time + block_duration
                logger.warning(f"IP {client_ip} blocked due to too many failed attempts")
                return jsonify({
                    'error': f'Too many failed attempts. Blocked for {block_duration} seconds.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def record_failed_attempt():
    """Record a failed authentication attempt"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    failed_attempts[client_ip].append(time.time())
    logger.warning(f"Failed authentication attempt from {client_ip}")

def clear_failed_attempts():
    """Clear failed attempts for successful login"""
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    if client_ip in failed_attempts:
        del failed_attempts[client_ip]
    if client_ip in blocked_ips:
        del blocked_ips[client_ip]

def require_2fa(f):
    """Decorator to require 2FA for sensitive operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('2fa_verified'):
            return jsonify({'error': '2FA verification required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def session_timeout_check(f):
    """Check for session timeout"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        last_activity = session.get('last_activity')
        if last_activity:
            timeout = current_app.config.get('SESSION_TIMEOUT', 7200)  # 2 hours
            if time.time() - last_activity > timeout:
                session.clear()
                return jsonify({'error': 'Session expired'}), 401
        
        session['last_activity'] = time.time()
        return f(*args, **kwargs)
    return decorated_function
