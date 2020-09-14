import bcrypt
import pytest
import uuid
import factory
import jwt

from flask import url_for, current_app
from json import dumps

from tests.factories.board import BoardFactory
from tests.factories.post import PostFactory
from tests.factories.user import UserFactory
from tests.factories.comment import CommentFactory
from app.models import Post, User


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


    class Describe_my_liked_post:
        @pytest.fixture
        def post(self, logged_in_user):
            return PostFactory.create(likes=[str(logged_in_user.id)])

        @pytest.fixture
        def subject(self, client, headers, post):
            url = url_for('UserView:my_liked_post')
            return client.get(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_내가_좋아한_글이_반환된다(self, subject, logged_in_user):
            body = subject.json

            assert body['total'] == 1

            post_id = body['items'][0]['id']
            assert str(logged_in_user.id) in Post.objects(id=post_id).get().likes

        class Context_다른_사용자가_좋아요를_누른경우:
            @pytest.fixture
            def another_user(self):
                return UserFactory.create()

            @pytest.fixture
            def post(self, another_user):
                return PostFactory.create(likes=[str(another_user.id)])

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_빈_list가_반환된다(self, subject):
                body = subject.json

                assert body['total'] == 0
                assert body['items'] == []

        class Context_로그인하지_않은경우:
            @pytest.fixture
            def logged_in_user(self):
                return None

            @pytest.fixture
            def another_user(self):
                return UserFactory.create()

            @pytest.fixture
            def post(self, another_user):
                return PostFactory.create(likes=[str(another_user.id)])

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401


    class Describe_signup:
        @pytest.fixture
        def form(self):
            return {
                "account": factory.Faker('name').generate(),
                "password": factory.Faker('password').generate()}

        @pytest.fixture
        def subject(self, client, headers, form):
            url = url_for('UserView:signup')
            return client.post(url, headers=headers, data=dumps(form))

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_user_갯수가_증가한다(self, subject):
            total_user_count = User.objects().count()
            assert total_user_count == 2

        def test_user_입력값과_동일하다(self, subject, form):
            account = User.objects()[1].account

            assert account == form['account']

        class Context_중복된_account로_회원가입하는경우:
            @pytest.fixture
            def form(self, logged_in_user):
                return {
                    "account": logged_in_user.account,
                    "password": factory.Faker('password').generate()}

            def test_409가_반환된다(self, subject):
                assert subject.status_code == 409

    class Describe_signin:

        @pytest.fixture
        def signup_user(self):
            return UserFactory.create(account='avery', password=bcrypt.hashpw('abc123'.encode('utf8'), bcrypt.gensalt()).decode('utf-8'))

        @pytest.fixture
        def form(self):
            return {
                "account": 'avery',
                "password": 'abc123'
            }

        @pytest.fixture(autouse=True)
        def subject(self, client, form, signup_user):
            url = url_for('UserView:signin')
            return client.post(url, data=dumps(form))


        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            # def test_토큰을_반환한다(self, subject, signup_user):
            #     body = subject.json
            #     assert body == dumps(jwt.encode({"user_id": dumps(signup_user.id), "is_master": signup_user.master_role},
            #                current_app.config['SECRET'], current_app.config['ALGORITHM']).decode('utf-8'))

        class Context_다른_계정으로_접근할경우:

            @pytest.fixture
            def form(self, form):
                form['account'] = 'dana'
                return form

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
                assert subject.json['message'] == '존재하지 않는 사용자입니다.'

        class Context_비밀번호가_틀린경우:

            @pytest.fixture
            def form(self, form):
                form['password'] = 'defg456'
                return form

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
                assert subject.json['message'] == '잘못된 비밀번호 입니다.'
