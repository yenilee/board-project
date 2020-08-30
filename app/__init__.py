import mongoengine

from flask      import Flask
from app.config import MONGO_URI

def create_app(TEST_CONFIG = None):
    app = Flask(__name__)
    app.debug = True

    try:
        mongoengine.connect(host=MONGO_URI)
    except Exception as e:
        print('Warning! 데이터베이스 에러 - ' + str(e))

    from flask_cors import CORS
    CORS(app, resources={r'*':{'origins':'*'}})

    from .views import register_api
    register_api(app)

    return app
