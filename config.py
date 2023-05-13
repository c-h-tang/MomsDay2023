class Config:
    DEBUG = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    ASSETS_DEBUG = False
    GUNICORN_TIMEOUT = 200

class ProductionConfig(Config):
 pass

class DevelopmentConfig(Config): 
 DEBUG = True
 DEVELOPMENT = True
 TEMPLATES_AUTO_RELOAD = True
 ASSETS_DEBUG = True