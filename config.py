"""
Configuration file for Phishing Email Detection System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/phishing_detector')

# Upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
ALLOWED_EXTENSIONS = {'eml', 'txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Model configuration
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'phishing_detector.pkl')
MODEL_VERSION = '1.0.0'

# API configuration
API_HOST = '0.0.0.0'
API_PORT = 5000
DEBUG = True

# ML Model parameters
ML_CONFIG = {
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    },
    'naive_bayes': {
        'alpha': 0.1
    },
    'test_size': 0.15,
    'cv_folds': 5,
    'target_accuracy': 0.90
}

# IOC extraction configuration
IOC_SEVERITY_RULES = {
    'high': ['md5', 'sha1', 'sha256'],
    'medium': ['ipv4', 'url'],
    'low': ['email', 'domain']
}

# Feature extraction
URGENCY_WORDS = [
    'urgent', 'immediately', 'action required', 'verify', 'suspend',
    'limited time', 'act now', 'confirm', 'expires', 'update', 'warning'
]

SUSPICIOUS_KEYWORDS = [
    'password', 'credit card', 'social security', 'bank account',
    'verify account', 'click here', 'winner', 'prize', 'lottery',
    'inheritance', 'transfer', 'refund', 'tax', 'suspended'
]

SUSPICIOUS_TLDS = [
    '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work',
    '.click', '.link', '.download', '.stream'
]

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
