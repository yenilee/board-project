import factory
import pytest
import arrow

from flask import url_for

from tests.factories.post import PostFactory
from tests.factories.user import UserFactory


class Describe_MainView:
    @pytest.fixture
    def post(self):
        return PostFactory.create()

    @pytest.fixture
    def logged_in_user(self):
        return UserFactory.create()

    class Describe_order_by_latest:
        @pytest.fixture
        def posts(self):
            PostFactory.create_batch(11)
            PostFactory.create(created_at=factory.Faker('date_between').generate())

        @pytest.fixture
        def subject(self, client, headers, posts):
            url = url_for('MainView:order_by_latest')
            return client.get(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_10개의_post_list가_반환된다(self, subject):
            body = subject.json

            assert len(body['posts']) == 10

        def test_post_list에_위쪽에_위치한_post의_create_time이_더_최근이다(self, subject):
            body = subject.json
            posts = body['posts']
            post_number = 0
            while post_number < 9:
                if posts[post_number]['created_at'] >= posts[post_number + 1]['created_at']:
                    post_number += 1
                elif posts[post_number]['created_at'] < posts[post_number + 1]['created_at']:
                    break
            assert post_number == 9


    class Describe_order_by_likes:

        @pytest.fixture
        def post(self):
            for n in range(1, 10):
                PostFactory.create()
            PostFactory.create(likes=['user1'])

        @pytest.fixture(autouse=True)
        def subject(self, client, post):
            url = url_for('MainView:order_by_likes')
            return client.get(url)

        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_10개의_post_list가_반환된다(self, subject):
                body = subject.json
                assert len(body["most_liked_posts"]) == 10

            def test_좋아요가_있는_게시물이_첫번째_인덱스로_반환된다(self, subject):
                body = subject.json
                assert body["most_liked_posts"][0]['total_likes_count'] == 1
                assert body["most_liked_posts"][1]['total_likes_count'] == 0

            def test_첫번째로_반환된_게시물의_좋아요가_가장_많다(self, subject, result=True):
                body = subject.json
                posts = body["most_liked_posts"]
                for index in range(1, 10):
                    if posts[index - 1]['total_likes_count'] < posts[index]['total_likes_count']:
                        result = False
                assert result == True

            class Context_좋아요가_더_많은_게시물이_생긴경우:

                @pytest.fixture
                def more_liked_post(self):
                    PostFactory.create(likes=['user1', 'user2', 'user3'])

                @pytest.fixture(autouse=True)
                def subject(self, client, post, more_liked_post):
                    url = url_for('MainView:order_by_likes')
                    return client.get(url)

                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_좋아요가_있는_게시물이_첫번째_인덱스로_반환된다(self, subject):
                    body = subject.json
                    assert body["most_liked_posts"][0]['total_likes_count'] == 3
                    assert body["most_liked_posts"][1]['total_likes_count'] == 1

                def test_첫번째로_반환된_게시물의_좋아요가_가장_많다(self, subject, result=True):
                    body = subject.json
                    posts = body["most_liked_posts"]
                    for index in range(1, 10):
                        if posts[index - 1]['total_likes_count'] < posts[index]['total_likes_count']:
                            result = False
                    assert result == True