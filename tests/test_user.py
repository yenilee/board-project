from unittest import mock
import pytest
import json
from mongoengine import connect, disconnect
from app import create_app
from config import test_config

connect('mongoenginetest', host='mongomock://localhost')

@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TESTING'] = True
    api = app.test_client()

    return api

def test_new_user(api):
    new_user = {
        'account': '2cong',
        'password': '1234'
    }
    resp = api.post(
        "user/signup",
        data = json.dumps(new_user),
        content_type = "application/json"
    )
    assert resp.status_code == 200
