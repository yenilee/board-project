import pytest
import uuid

from flask import url_for

from tests.factories.board import BoardFactory
from tests.factories.post import PostFactory
from tests.factories.user import UserFactory
from tests.factories.comment import CommentFactory


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

    @pytest.fixture
    def comment(self):
        return CommentFactory.create()


    class Describe_my_posts:

        @pytest.fixture(autouse=True)
        def subject(self, client, headers, post):
            url = url_for('UserView:my_posts')
            return client.get(url, headers=headers)

        class Context_정상요청:

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_사용자의_게시글이_반환된다(self, subject, post, logged_in_user):
                body = subject.json
                assert body['total'] == 1
                assert body['items'][0]['author']['id'] == str(logged_in_user.id)
                assert body['items'][0]['id'] == str(post.id)

        class Context_다른_사용자가_게시글을_작성한경우:

            @pytest.fixture
            def post(self):
                return PostFactory.create()

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_빈_글목이_반환된다(self, subject):
                body = subject.json
                assert body['total'] == 0


        class Context_비로그인_사용자가_마이페이지에_접근하는경우:

            @pytest.fixture
            def post(self):
                return PostFactory.create()

            @pytest.fixture
            def logged_in_user(self):
                return None

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
                assert subject.json['message'] == '로그인하지 않은 사용자입니다.'

            class Context_유효하지_않은_토큰경우:
                @pytest.fixture
                def token(self):
                    return uuid.uuid4()

                def test_401이_반환된다(self, subject):
                    assert subject.status_code == 401
                    assert subject.json['message'] == '유효하지 않은 토큰입니다'


    class Describe_my_comments:

        @pytest.fixture
        def comment(self, logged_in_user):
            return CommentFactory.create(author=logged_in_user.id)

        @pytest.fixture(autouse=True)
        def subject(self, client, headers, comment):
            url = url_for('UserView:my_comments')
            return client.get(url, headers=headers)

        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_사용자의_댓글이_반환된다(self, subject, comment, logged_in_user):
                body = subject.json
                assert body['total'] == 1
                assert body['items'][0]['author']['id'] == str(logged_in_user.id)
                assert body['items'][0]['content'] == comment.content

        class Context_비로그인_사용자가_마이페이지에_접근하는경우:

            @pytest.fixture
            def comment(self):
                return CommentFactory.create()

            @pytest.fixture
            def logged_in_user(self):
                return None

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
                assert subject.json['message'] == '로그인하지 않은 사용자입니다.'

            class Context_유효하지_않은_토큰경우:
                @pytest.fixture
                def token(self):
                    return uuid.uuid4()

                def test_401이_반환된다(self, subject):
                    assert subject.status_code == 401
                    assert subject.json['message'] == '유효하지 않은 토큰입니다'

        class Context_다른_사용자가_댓글을_작성한경우:

            @pytest.fixture
            def comment(self):
                return CommentFactory.create()

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_빈_글목이_반환된다(self, subject):
                body = subject.json
                assert body['total'] == 0
