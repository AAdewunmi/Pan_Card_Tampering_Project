import os


class Config(object):

    DEBUG = False
    TESTING = False
    basedir = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = 'pianalytix'

    UPLOADS = "/home/username/app/app/static/uploads"

    SESSION_COOKIE_SECURE = True
    DEFAULT_THEME = None


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class DebugConfig(Config):
    DEBUG = False


class DefaultConfig:
    DEBUG = True
    SECRET_KEY = "your_secret_key"
    # Add other configuration variables as needed
