#!/usr/bin/env python3
"""
Configuration settings for Folktale Reader application
"""

import os
from pathlib import Path

# Get the base directory (root of the project)
BASE_DIR = Path(__file__).parent.parent.absolute()

# Database configuration
DATABASE_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "folktale_users.db"

# Data files
DATA_DIR = BASE_DIR / "data"
STORIES_DATA_PATH = DATA_DIR / "stories_data.json"

# Assets directory
ASSETS_DIR = BASE_DIR / "assets"

# Templates and static files
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Flask configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
# Security settings for production
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @staticmethod
    def validate():
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY environment variable must be set in production")

# Development settings
class DevelopmentConfig(Config):
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
