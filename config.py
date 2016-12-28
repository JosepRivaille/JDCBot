class Config(object):
    SECRET_KEY = 'my_secret_token'  # Set here your secret key
    PAGE_ACCESS_TOKEN = 'facebook_token'  # Set here facebook token


class DevelopmentConfig(Config):
    DEBUG = True
