import jwt
from flask import current_app
from jedi.plugins import pytest
from bson.json_util import dumps as bson_dumps


@pytest.fixture
def token(logged_in_user):
    if logged_in_user:
        return jwt.encode({"user_id": bson_dumps(logged_in_user.id),
                        "is_master": logged_in_user.master_role},
                       current_app.config['SECRET'],
                       current_app.config['ALGORITHM'])
    else:
        return None


@pytest.fixture
def headers(token):
    headers = {
        'Authorization': token
    }
    return headers

