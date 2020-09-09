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
        def subject(self, client, logged_in_user, post):
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


    class Describe_Post:
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
        def subject(self, client, form, logged_in_user, post):
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


    class Describe_Update:
        @pytest.fixture
        def post(self):
            return PostFactory.create()

        @pytest.fixture
        def logged_in_user(self):
            return UserFactory.create()

        @pytest.fixture
        def form(self):
            return {'content': factory.Faker('sentence').generate()}

        class Describe_Update_With_No_Auth:
            @pytest.fixture
            def comment(self, post):
                comment = CommentFactory.create(post=post)
                return comment

            @pytest.fixture
            def subject(self, client, form, logged_in_user, post, comment):
                url = url_for('CommentView:update', board_id=post.board.id, post_id=post.id, comment_id=comment.id)

                token = jwt.encode({"user_id": dumps(str(logged_in_user.id)),
                                    "is_master": logged_in_user.master_role}, current_app.config['SECRET'], current_app.config['ALGORITHM'])
                headers = {
                    'Authorization': token
                }

                return client.put(url, headers=headers, data=dumps(form))

            def test_403이_반환된다(self, subject):
                assert subject.status_code == 403

        class Describe_Update_With_Master_Auth:
            @pytest.fixture
            def logged_in_master(self):
                return MasterUserFactory.create()

            @pytest.fixture
            def comment(self, post):
                comment = CommentFactory.create(post=post)
                return comment

            @pytest.fixture
            def subject(self, client, form, logged_in_master, post, comment):
                url = url_for('CommentView:update', board_id=post.board.id, post_id=post.id,
                              comment_id=comment.id)

                token = jwt.encode({"user_id": dumps(str(logged_in_master.id)),
                                    "is_master": logged_in_master.master_role}, current_app.config['SECRET'],
                                   current_app.config['ALGORITHM'])
                headers = {
                    'Authorization': token
                }

                return client.put(url, headers=headers, data=dumps(form))

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_content_내용이_변경된다(self, subject, form):
                content = Comment.objects().get().content
                assert content == form['content']