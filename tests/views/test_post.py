import jwt
import pytest
import factory

from flask import url_for, current_app
from bson.json_util import dumps as bson_dumps
from json import dumps as json_dumps

from app.models import Post
from tests.factories.post import PostFactory
from tests.factories.user import UserFactory
from tests.factories.board import BoardFactory


class Describe_PostView:

        @pytest.fixture
        def board(self):
            return BoardFactory.create()

        @pytest.fixture
        def logged_in_user(self):
            return UserFactory.create()

        class Describe_post:

            @pytest.fixture
            def form(self):
                return {
                    "title" : factory.Faker('sentence').generate(),
                    "content" : factory.Faker('sentence').generate()
                }

            @pytest.fixture(autouse=True)
            def subject(self, client, form, logged_in_user, board):
                url = url_for('PostView:post', board_id=board.id)

                token = jwt.encode({"user_id": bson_dumps(logged_in_user.id),
                                    "is_master": logged_in_user.master_role},
                                   current_app.config['SECRET'],
                                   current_app.config['ALGORITHM'])
                headers = {
                    'Authorization': token
                }
                return client.post(url, headers = headers, data=json_dumps(form))

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_게시글이_추가된다(self, subject):
                assert Post.objects.count() == 1

            # class Context_비로그인_사용자가_생성하는경우:



        # @pytest.fixture
       # def test_post의_like한_user가_추가된다(self, subject, post, logged_in_user):
        #     post.reload()
        #     assert logged_in_user in post.likes
        #
        # class Context_이미_like한경우:
        #     @pytest.fixture
        #     def post(self, post, logged_in_user):
        #         post.likes.create(logged_in_user)
        #         return post
        #
        #     @pytest.fixture
        #     def test_200이_반환된다(self, subject):
        #         assert subject.status_code == 200
        #
        #     @pytest.fixture
        #     def test_아무일도_일어나지_않는다(self, subject, post, logged_in_user):
        #         post.reload()
        #         like_users = post.likes.filter(lambda user: user == logged_in_user)
        #         assert len(like_users) == 1
