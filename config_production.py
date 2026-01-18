import os
from config import Config

class ProductionConfig(Config):
    """Production configuration"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Database - use PostgreSQL or MySQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             os.environ.get('SQLALCHEMY_DATABASE_URI') or \
                             'sqlite:///smart_doc_extractor.db'
    
    # Disable debug mode
    DEBUG = False
    TESTING = False
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # File upload security
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Server configuration
    SERVER_NAME = os.environ.get('SERVER_NAME')  # e.g., 'yourdomain.com'
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def validate_production_config(cls):
        """Validate required production settings"""
        errors = []
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your-secret-key-here-change-in-production':
            errors.append("SECRET_KEY must be set to a secure random value")
        
        if 'sqlite' in cls.SQLALCHEMY_DATABASE_URI.lower():
            print("WARNING: Using SQLite in production. Consider using PostgreSQL or MySQL.")
        
        if errors:
            raise ValueError("Production configuration errors:\n" + "\n".join(f"- {e}" for e in errors))
        
        return True
