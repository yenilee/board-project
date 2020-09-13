from json import dumps
import factory
import pytest
import arrow
from flask import url_for

from tests.factories.board import BoardFactory, DeletedBoardFactory
from tests.factories.user import UserFactory, MasterUserFactory
from tests.factories.post import PostFactory, DeletedPostFactory
from app.models import Board, Post


class Describe_BoardView:
    @pytest.fixture
    def logged_in_user(self):
        return MasterUserFactory.create()

    @pytest.fixture
    def board(self):
        return BoardFactory.create()

    class Describe_get_category:
        @pytest.fixture
        def subject(self, client, headers, board):
            url = url_for('BoardView:get_category')
            return client.get(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_board_list가_반환된다(self, subject, board):
            body = subject.json

            assert body['category'][0]['name'] == board.name
            assert body['category'][0]['id'] == str(board.id)

        class Context_board가_없는_경우:
            @pytest.fixture
            def board(self):
                return None

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_빈_list가_반환된다(self, subject, board):
                body = subject.json

                assert body['category'] == []

        class Context_board_가_soft_delete상태인_경우:
            @pytest.fixture
            def board(self):
                return DeletedBoardFactory.create()

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_빈_list가_반환된다(self, subject, board):
                body = subject.json

                assert body['category'] == []


    class Describe_post:
        @pytest.fixture
        def form(self):
            return {'name': factory.Faker('sentence').generate()}

        @pytest.fixture
        def subject(self, client, headers, form):
            url = url_for('BoardView:post')
            return client.post(url, headers=headers, data=dumps(form))

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_board이름이_입력값과_동일하다(self, subject, form):
            board_name = Board.objects().get().name
            assert board_name == form['name']

        def test_board_갯수가_증가한다(self, subject):
            total_board_count = Board.objects().count()
            assert total_board_count == 1

        class Context_user가_마스터가_아닌_경우:
            @pytest.fixture
            def logged_in_user(self):
                return UserFactory.create()

            def test_403이_반환된다(self, subject):
                assert subject.status_code == 403

        class Context_name이_입력되지_않은경우:
            @pytest.fixture
            def form(self):
                return {'name': ''}

            def test_422가_반환된다(self, subject):
                assert subject.status_code == 422

        class Context_중복된_이름으로_생성하려고_하는경우:
            @pytest.fixture
            def form(self, board):
                return {'name': board.name}

            def test_400이_반환된다(self, subject):
                assert subject.status_code == 400

            class Context_중복된_이름의_게시판이_soft_delete된_경우:
                @pytest.fixture
                def board(self):
                    return DeletedBoardFactory.create()

                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_board_갯수가_증가한다(self, subject):
                    total_board_count = Board.objects().count()
                    assert total_board_count == 2


    class Describe_get:
        @pytest.fixture
        def post(self, board):
            return PostFactory.create(board=board)

        @pytest.fixture
        def subject(self, client, headers, board, post):
            url = url_for('BoardView:get', board_id=board.id)
            return client.get(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_게시글_list가_반환된다(self, subject, post):
            body = subject.json

            assert body['total'] == 1
            assert body['items'][0]['title'] == post.title

        class Context_board에_post가_없는_경우:
            @pytest.fixture
            def post(self):
                return None

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_빈_list가_반환된다(self, subject):
                body = subject.json

                assert body['total'] == 0
                assert body['items'] == []

        class Context_board_가_soft_delete상태인_경우:
            @pytest.fixture
            def post(self, board):
                return DeletedPostFactory.create(board=board)

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_빈_list가_반환된다(self, subject):
                body = subject.json

                assert body['total'] == 0
                assert body['items'] == []
