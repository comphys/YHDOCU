class Config(object):
    DEBUG = True
    ENV = 'development'
    SECRET_KEY = 'JungYhKimJhJungYj'


class ProductionConfig(object):
    ENV = 'Production'
    DEBUG = False
    SECRET_KEY = 'JungYhKimJhJungYj'