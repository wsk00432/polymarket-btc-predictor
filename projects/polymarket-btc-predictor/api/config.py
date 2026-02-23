"""
API Configuration
"""

import os
from datetime import timedelta

class BaseConfig:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'btc-predictor-secret-key')
    API_KEY = os.environ.get('API_KEY', 'btc-predictor-api-key')
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_DEFAULT = '100 per hour'
    RATE_LIMIT_STORAGE_URL = 'memory://'
    
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'predictions.db')
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    # CORS
    CORS_ORIGINS = ['*']

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_DEFAULT = '1000 per hour'

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    RATE_LIMIT_ENABLED = False

config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
