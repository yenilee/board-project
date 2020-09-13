from json import dumps as json_dumps

import factory
import pytest
from flask import url_for

from app.models import Post
from tests.factories.board import BoardFactory, DeletedBoardFactory
from tests.factories.post import DeletedPostFactory, PostFactory
from tests.factories.user import MasterUserFactory, UserFactory


class Describe_UserView:
    @pytest.fixture
    def board(self):
        return BoardFactory.create()

    @pytest.fixture
    def logged_in_user(self):
        return UserFactory.create()

    @pytest.fixture
    def post(self, board, logged_in_user):
        return PostFactory.create(board=board.id, author=logged_in_user.id)

    class Describe_my_post:

        @pytest.fixture(autouse=True)
        def subject(self, client, headers):
            url = url_for('UserView:my_post')
            return client.get(url, headers=headers)

        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200