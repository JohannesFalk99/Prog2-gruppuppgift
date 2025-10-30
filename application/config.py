import os
from pathlib import Path

class Config:
    """Base configuration class"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    # Cookie settings
    COOKIE_CONSENT_DAYS = 365
    COOKIE_USER_ID_DAYS = 365

    # API settings
    ELPRISER_API_BASE_URL = "https://www.elprisetjustnu.se/api/v1/prices"
    ALLOWED_PRISKLASSER = ['SE1', 'SE2', 'SE3', 'SE4']

    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration"""
        app.config.from_object(cls)

        # Ensure project directories exist
        cls.PROJECT_ROOT.mkdir(parents=True, exist_ok=True)

        # Set up logging if needed
        if not app.debug and not app.testing:
            # Production logging setup could go here
            pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{Config.PROJECT_ROOT / "annotations.db"}'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # In production, require environment variables
    @classmethod
    def init_app(cls, app):
        super().init_app(app)

        # Ensure required environment variables are set
        required_vars = ['SECRET_KEY']
        for var in required_vars:
            if not os.environ.get(var):
                raise ValueError(f"Required environment variable {var} is not set")


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV') or 'development'

    return config.get(config_name, config['default'])
