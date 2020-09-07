import pytest

from flask import current_app


@pytest.fixture(scope="session")
def app():
    from app import create_app
    app = create_app()
    return app


@pytest.fixture(scope='function', autouse=True)
def db(app):
    import mongoengine
    mongoengine.connect(host=current_app.config['MONGO_URI'])
    yield
    mongoengine.disconnect()
