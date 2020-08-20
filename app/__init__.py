import mongoengine

from flask      import Flask
from app.config import MONGO_URI

def create_app():
    app = Flask(__name__)
    app.debug = True

    mongoengine.connect(host=MONGO_URI)

    from flask_cors import CORS
    CORS(app, resources={r'*':{'origins':'*'}})

    from .views import register_api
    register_api(app)

    return app

