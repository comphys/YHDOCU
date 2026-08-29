class Config(object):
    DEBUG = True
    SECRET_KEY = 'JungYhKimJhJungYj'
    PERMANENT_SESSION_LIFETIME = 864000
    JSON_AS_ASCII = False


class ProductionConfig(object):
    DEBUG = False
    SECRET_KEY = 'JungYhKimJhJungYj'
    PERMANENT_SESSION_LIFETIME = 864000
    JSON_AS_ASCII = False