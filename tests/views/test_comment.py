from json import dumps

import jwt
import pytest
from flask import current_app, url_for

from tests.factories.post import PostFactory
from tests.factories.user import UserFactory


class Describe_CommentView:
    class Describe_index:
        @pytest.fixture
        def post(self):
            return PostFactory.create()

        @pytest.fixture
        def logged_in_user(self):
            return UserFactory.create()

        @pytest.fixture
        def subject(self, client, logged_in_user, post):
            url = url_for('CommentView:index', board_id=post.board.id, post_id=post.id)

            token = jwt.encode({"user_id": dumps(str(logged_in_user.id)),
                                "is_master": False}, current_app.config['SECRET'], current_app.config['ALGORITHM'])
            headers = {
                'Authorization': token
            }

            return client.get(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_빈_list가_반환된다(self, subject):
            body = subject.json

            assert body['total'] == 0
            assert body['items'] == []