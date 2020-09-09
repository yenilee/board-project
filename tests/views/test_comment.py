from json import dumps

import factory
import jwt
import pytest
from flask import current_app, url_for

from tests.factories.post import PostFactory
from tests.factories.user import UserFactory, MasterUserFactory
from tests.factories.comment import CommentFactory
from app.models import Comment


class Describe_CommentView:
    class Describe_index:
        @pytest.fixture
        def post(self):
            return PostFactory.create()

        @pytest.fixture
        def logged_in_user(self):
            return UserFactory.create()

        @pytest.fixture
        def subject(self, client, headers, logged_in_user, post):
            url = url_for('CommentView:index', board_id=post.board.id, post_id=post.id)

            token = jwt.encode({"user_id": dumps(str(logged_in_user.id)),
                                "is_master": logged_in_user.master_role}, current_app.config['SECRET'], current_app.config['ALGORITHM'])
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


    class Describe_post:
        @pytest.fixture
        def post(self):
            return PostFactory.create()

        @pytest.fixture
        def logged_in_user(self):
            return UserFactory.create()

        @pytest.fixture
        def form(self):
            return {'content': factory.Faker('sentence').generate()}

        @pytest.fixture
        def subject(self, client, post, form, logged_in_user):
            url = url_for('CommentView:post', board_id=post.board.id, post_id=post.id)

            token = jwt.encode({"user_id": dumps(str(logged_in_user.id)),
                                "is_master": logged_in_user.master_role}, current_app.config['SECRET'], current_app.config['ALGORITHM'])
            headers = {
                'Authorization': token
            }

            return client.post(url, headers=headers, data=dumps(form))

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_comment_갯수가_증가한다(self, subject):
            total_comment_count = Comment.objects().count()
            assert total_comment_count == 1

        def test_comment가_입력값과_동일하다(self, subject, form):
            content = Comment.objects().get().content
            assert content == form['content']


    class Describe_update:
        @pytest.fixture
        def post(self):
            return PostFactory.create()

        @pytest.fixture
        def logged_in_user(self):
            return UserFactory.create()

        @pytest.fixture
        def form(self):
            return {'content': factory.Faker('sentence').generate()}

        @pytest.fixture
        def comment(self, post, logged_in_user):
            return CommentFactory.create(post=post, author=logged_in_user)

        @pytest.fixture
        def subject(self, client, post, comment, form, logged_in_user):
            url = url_for('CommentView:update', board_id=post.board.id, post_id=post.id, comment_id=comment.id)

            token = jwt.encode({"user_id": dumps(str(logged_in_user.id)),
                                "is_master": logged_in_user.master_role}, current_app.config['SECRET'], current_app.config['ALGORITHM'])
            headers = {
                'Authorization': token
            }

            return client.put(url, headers=headers, data=dumps(form))

        def test_200이반환된다(self, subject):
            assert subject.status_code == 200

        class Context_content가_입력되지_않은경우:
            @pytest.fixture
            def form(self):
                return {'content': ''}

            def test_422이_반환된다(self, subject):
                assert subject.status_code == 422

        class Context_로그인한_사용자가_Comment_작성자가_아닌경우:
            @pytest.fixture
            def comment(self, post):
                return CommentFactory.create(post=post)

            def test_403이_반환된다(self, subject):
                assert subject.status_code == 403

            class Context_Master계정인경우:
                @pytest.fixture
                def logged_in_user(self):
                    return MasterUserFactory.create()

                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_content_내용이_변경된다(self, subject, form):
                    content = Comment.objects().get().content
                    assert content == form['content']
