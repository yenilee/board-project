import os
import mongoengine

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.debug = True
    phase = os.environ.get('PHASE', 'local').lower()

    try:
        app.config.from_object('app.config.%sConfig' % phase.capitalize())
        mongoengine.connect(host=app.config['MONGO_URI'])
    except Exception as e:
        print('Warning! 데이터베이스 에러 - ' + str(e))

    from flask_cors import CORS
    CORS(app, resources={r'*': {'origins': '*'}})

    from .views import register_api
    register_api(app)

    return app
