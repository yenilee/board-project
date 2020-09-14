import factory
import pytest
import random

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
            PostFactory.create_batch(11, created_at=factory.Faker('date_between').generate())

        @pytest.fixture
        def recent_post(self):
            return PostFactory.create(created_at=arrow.utcnow().format('YYYY-MM-DD HH:mm:ss'))

        @pytest.fixture
        def subject(self, client, headers, posts, recent_post):
            url = url_for('MainView:order_by_latest')
            return client.get(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_10개의_post_list가_반환된다(self, subject):
            body = subject.json

            assert len(body['posts']) == 10

        def test_post_list에서_첫번째_post가_제일_최근에_생성된_post이다(self, subject, recent_post):
            body = subject.json
            latest_post = body['posts'][0]

            assert latest_post['title'] == recent_post.title
            assert latest_post['id'] == str(recent_post.id)

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
        def users(self):
            return UserFactory.create_batch(10)

        @pytest.fixture
        def posts(self, users):
            for _ in range(0,10):
                number_of_likes = random.randint(0, 10)
                random_users = random.sample(users, k=number_of_likes)
                PostFactory.create(likes=[str(user.id) for user in random_users])

        @pytest.fixture(autouse=True)
        def subject(self, client, posts):
            url = url_for('MainView:order_by_likes')
            return client.get(url)

        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_10개의_post_list가_반환된다(self, subject):
                body = subject.json
                assert len(body['posts']) == 10

            def test_첫번째로_반환된_게시물의_좋아요가_가장_많다(self, subject):
                body = subject.json
                posts = body["posts"]
                result = 0
                for index in range(1, 10):
                    if posts[index-1]['total_likes_count'] < posts[index]['total_likes_count']:
                        print(posts[index-1]['total_likes_count'])
                        result += 1
                assert result == 0