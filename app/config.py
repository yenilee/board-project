class Config:
    SECRET = 'hiitssecret'
    ALGORITHM = 'HS256'
    TESTING = False
    MONGO_URI = 'mongodb://localhost:27017/board_test'

class LocalConfig(Config):
    MONGO_URI = 'mongodb://localhost:27017/board_test'
    TESTING = True
    DEBUG = True

class TestConfig(Config):
    MONGO_URI = 'mongomock://127.0.0.1:27017/board_test?connect=false'
    TESTING = True




