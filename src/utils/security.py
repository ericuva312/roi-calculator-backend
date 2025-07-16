"""
Security utilities for ROI Calculator Backend
"""
import re
import time
import hashlib
import logging
from functools import wraps
from flask import request, jsonify
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: deque())

def rate_limit(max_requests=10, window_minutes=1):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = time.time()
            window_seconds = window_minutes * 60
            
            # Clean old requests
            while (rate_limit_storage[client_ip] and 
                   current_time - rate_limit_storage[client_ip][0] > window_seconds):
                rate_limit_storage[client_ip].popleft()
            
            # Check rate limit
            if len(rate_limit_storage[client_ip]) >= max_requests:
                log_security_event('rate_limit_exceeded', f'IP: {client_ip}')
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window_minutes} minute(s)'
                }), 429
            
            # Add current request
            rate_limit_storage[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(data):
    """Sanitize input data to prevent XSS and injection attacks"""
    if isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\']', '', data)
        # Limit length
        return data[:1000]
    return data

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone format"""
    if not phone:
        return True  # Phone is optional
    # Remove all non-digits
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a reasonable length
    return 10 <= len(digits_only) <= 15

def validate_url(url):
    """Validate URL format"""
    if not url:
        return True  # URL is optional
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    return re.match(pattern, url) is not None

def encrypt_sensitive_data(data):
    """Simple encryption for sensitive data"""
    if not data:
        return data
    # In production, use proper encryption
    return hashlib.sha256(data.encode()).hexdigest()[:16] + "***"

def log_security_event(event_type, details):
    """Log security events"""
    logger.warning(f"Security Event: {event_type} - {details}")

def enforce_https():
    """Enforce HTTPS in production"""
    if request.headers.get('X-Forwarded-Proto') == 'http':
        return jsonify({'error': 'HTTPS required'}), 403
    return None
