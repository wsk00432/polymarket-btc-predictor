"""
BTC Predictor API - Modular REST API
Version 2.0 - Refactored with Flask Blueprints
"""

from flask import Flask, jsonify, request, g
from flask_cors import CORS
import logging
import json
import os
from datetime import datetime

# Import blueprints
from api.routes.predictions import predictions_bp
from api.routes.outcomes import outcomes_bp
from api.routes.digests import digests_bp
from api.routes.stats import stats_bp
from api.middleware.auth import auth_middleware
from api.middleware.rate_limit import rate_limit_middleware

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(config_name: str = 'default'):
    """
    Application factory for BTC Predictor API
    
    Args:
        config_name: Configuration name (default, production, development)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(f'api.config.{config_name}')
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register middleware
    app.before_request(auth_middleware)
    app.before_request(rate_limit_middleware)
    
    # Register blueprints
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(outcomes_bp, url_prefix='/api/outcomes')
    app.register_blueprint(digests_bp, url_prefix='/api/digests')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        })
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'name': 'BTC Predictor API',
            'version': '2.0.0',
            'endpoints': {
                'predictions': '/api/predictions',
                'outcomes': '/api/outcomes',
                'digests': '/api/digests',
                'stats': '/api/stats',
                'health': '/api/health'
            },
            'docs': '/api/docs'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    logger.info(f"BTC Predictor API v2.0.0 initialized ({config_name} mode)")
    
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=8080, debug=True)
