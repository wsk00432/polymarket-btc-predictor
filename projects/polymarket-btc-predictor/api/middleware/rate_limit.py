"""
Rate Limiting Middleware
"""

from flask import request, jsonify, current_app, g
from datetime import datetime, timedelta
import time

# Simple in-memory rate limiting storage
rate_limit_store = {}

def rate_limit_middleware():
    """
    Rate limiting middleware
    
    Limits requests per IP address
    """
    if not current_app.config.get('RATE_LIMIT_ENABLED', True):
        return None
    
    # Get client IP
    client_ip = request.remote_addr or 'unknown'
    
    # Parse rate limit config (format: "X per Y")
    rate_limit_str = current_app.config.get('RATE_LIMIT_DEFAULT', '100 per hour')
    try:
        limit_count, limit_period = rate_limit_str.split(' per ')
        limit_count = int(limit_count)
        limit_seconds = 3600 if 'hour' in limit_period else 60 if 'minute' in limit_period else 86400
    except:
        limit_count = 100
        limit_seconds = 3600
    
    # Get or create rate limit entry for this IP
    now = time.time()
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = {'count': 0, 'reset': now + limit_seconds}
    
    entry = rate_limit_store[client_ip]
    
    # Check if window has reset
    if now > entry['reset']:
        entry['count'] = 0
        entry['reset'] = now + limit_seconds
    
    # Increment count
    entry['count'] += 1
    
    # Check if limit exceeded
    if entry['count'] > limit_count:
        retry_after = int(entry['reset'] - now)
        response = jsonify({
            'error': 'Rate limit exceeded',
            'retry_after': retry_after
        })
        response.status_code = 429
        response.headers['Retry-After'] = str(retry_after)
        return response
    
    # Add rate limit headers to response (will be added by after_request)
    g.rate_limit_remaining = limit_count - entry['count']
    g.rate_limit_reset = int(entry['reset'])
    
    return None

def add_rate_limit_headers(response):
    """Add rate limit headers to response"""
    if hasattr(g, 'rate_limit_remaining'):
        response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_remaining)
    if hasattr(g, 'rate_limit_reset'):
        response.headers['X-RateLimit-Reset'] = str(g.rate_limit_reset)
    return response
