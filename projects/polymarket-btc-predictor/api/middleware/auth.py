"""
Authentication Middleware
"""

from flask import request, jsonify, current_app, g
from functools import wraps

def auth_middleware():
    """
    API Key authentication middleware
    
    Expects API key in header: X-API-Key
    Or query param: api_key
    """
    # Skip auth for health check
    if request.path == '/api/health' or request.path == '/':
        return None
    
    # Get API key from header or query param
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    
    # Get expected API key from config
    expected_key = current_app.config.get('API_KEY', 'btc-predictor-api-key')
    
    # Check if API key matches
    if api_key and api_key == expected_key:
        g.authenticated = True
        g.api_key = api_key
        return None
    
    # For now, allow unauthenticated access (can be enabled later)
    g.authenticated = False
    return None

def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.get('authenticated', False):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated
