import factory
import pytest
import uuid

from flask import url_for
from json import dumps as json_dumps

from app.models import Post
from tests.factories.board import BoardFactory, DeletedBoardFactory
from tests.factories.post import DeletedPostFactory, PostFactory
from tests.factories.user import MasterUserFactory, UserFactory


class Describe_PostView:
    @pytest.fixture
    def board(self):
        return BoardFactory.create()

    @pytest.fixture
    def logged_in_user(self):
        return UserFactory.create()

    @pytest.fixture
    def post(self, board, logged_in_user):
        return PostFactory.create(board=board.id, author=logged_in_user.id)

    class Describe_post:
        @pytest.fixture
        def form(self):
            return {
                "title": factory.Faker('sentence').generate(),
                "content": factory.Faker('sentence').generate(),
                "tags": ["tags"]
            }

        @pytest.fixture(autouse=True)
        def subject(self, client, headers, form, board):
            url = url_for('PostView:post', board_id=board.id)
            return client.post(url, headers=headers, data=json_dumps(form))

        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_게시글이_추가된다(self, subject, form, logged_in_user):
                assert Post.objects.count() == 1
                post = Post.objects.first()
                assert post.title == form['title']
                assert post.content == form['content']
                assert post.tags == form['tags']
                assert post.author.id == logged_in_user.id

        class Context_요청이_유효하지_않은경우:
            class Context_title이_없는경우:

                @pytest.fixture
                def form(self, form):
                    form.pop('title')
                    return form

                def test_422가_반환된다(self, subject):
                    assert subject.status_code == 422

            class Context_tag의_type이_유효하지_않은경우:

                @pytest.fixture
                def form(self, form):
                    form['tags'] = 123
                    return form

                def test_422가_반환된다(self, subject):
                    assert subject.status_code == 422

        class Context_비로그인_사용자가_게시글을_생성하는경우:
            @pytest.fixture
            def post(self, board):
                return PostFactory.create(board=board.id)

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

        class Context_없는_게시판에_게시글을_생성하는_경우:
            @pytest.fixture
            def board(self):
                return DeletedBoardFactory.create()

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404
                assert subject.json['message'] == '없는 게시판입니다.'

    class Describe_get:
        @pytest.fixture(autouse=True)
        def subject(self, client, post):
            url = url_for('PostView:get', board_id=post.board.id, post_id=post.id)
            return client.get(url)

        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_조회한_게시글이_요청_리소스와_동일하다(self, subject, post):
                assert subject.json['id'] == str(post.id)

        class Context_조회요청_게시판이_없는경우:
            @pytest.fixture
            def board(self):
                return DeletedBoardFactory.create()

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404
                assert subject.json['message'] == '없는 게시판입니다.'

        class Context_조회요청_게시글이_없는경우:
            @pytest.fixture
            def post(self):
                return DeletedPostFactory.create()

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404
                assert subject.json['message'] == '없는 게시물입니다.'

    class Describe_update:

        @pytest.fixture
        def form(self):
            return {"tags": ["updated_tag"]}

        @pytest.fixture(autouse=True)
        def subject(self, client, headers, post, form):
            url = url_for('PostView:update', board_id=post.board.id, post_id=post.id)
            return client.put(url, headers=headers, data=json_dumps(form))

        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_게시글이_수정된다(self, subject, post, form):
                post.reload()
                assert post.tags == form["tags"]

        class Context_요청_key값이_유효하지_않은경우:

            @pytest.fixture
            def form(self, form):
                form.pop("tags")
                form["tag"] = ["wrong_key"]
                return form

            def test_422가_반환된다(self, subject):
                assert subject.status_code == 422

        class Context_수정요청_게시판이_없는경우:
            @pytest.fixture
            def board(self):
                return DeletedBoardFactory.create()

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404
                assert subject.json['message'] == '없는 게시판입니다.'

        class Context_수정요청_게시글이_없는경우:
            @pytest.fixture
            def post(self, board):
                return DeletedPostFactory.create(board=board.id)

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404
                assert subject.json['message'] == '없는 게시물입니다.'

        class Context_비로그인_사용자가_게시글을_수정하는경우:

            @pytest.fixture
            def post(self, board):
                return PostFactory.create(board=board.id)

            @pytest.fixture
            def logged_in_user(self):
                return None

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
                assert subject.json['message'] == '로그인하지 않은 사용자입니다.'

            class Context_유효하지_않은_토큰으로_수정할경우:

                @pytest.fixture
                def token(self):
                    return uuid.uuid4()

                def test_401이_반환된다(self, subject):
                        assert subject.status_code == 401
                        assert subject.json['message'] == '유효하지 않은 토큰입니다'

        class Context_로그인_사용자가_게시글_작성자가_아닌경우:

            @pytest.fixture
            def post(self):
                return PostFactory.create()

            def test_403이_반환된다(self, subject):
                assert subject.status_code == 403

            class Context_로그인_사용자가_마스터일경우:

                @pytest.fixture
                def logged_in_user(self):
                    return MasterUserFactory.create()

                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_게시글이_수정된다(self, subject, post, form):
                    post.reload()
                    assert post.tags == form['tags']

    class Describe_delete:

        @pytest.fixture(autouse=True)
        def subject(self, client, headers, post):
            url = url_for('PostView:delete', board_id=post.board.id, post_id=post.id)
            return client.delete(url, headers=headers)

        class Context_정상요청:
            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_게시글이_삭제된다(self, subject, post):
                assert post.is_deleted == False
                post.reload()
                assert post.is_deleted == True

        class Context_삭제요청_게시판이_없는경우:
            @pytest.fixture
            def board(self):
                return DeletedBoardFactory.create()

            def test_404가_반환된다(self, subject, post):
                assert subject.status_code == 404
                assert subject.json['message'] == '없는 게시판입니다.'

        class Context_삭제요청_게시글이_없는경우:
            @pytest.fixture
            def post(self, board):
                return DeletedPostFactory.create(board=board.id)

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404
                assert subject.json['message'] == '없는 게시물입니다.'

        class Context_비로그인_사용자가_게시글을_삭제하는경우:
            @pytest.fixture
            def post(self, board):
                return PostFactory.create(board=board.id)

            @pytest.fixture
            def logged_in_user(self):
                return None

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
                assert subject.json['message'] == '로그인하지 않은 사용자입니다.'

            class Context_유효하지_않은_토큰으로_삭제할경우:

                @pytest.fixture
                def token(self):
                    return uuid.uuid4()

                def test_401이_반환된다(self, subject):
                        assert subject.status_code == 401
                        assert subject.json['message'] == '유효하지 않은 토큰입니다'

        class Context_로그인_사용자가_게시글_작성자가_아닌경우:

            @pytest.fixture
            def post(self, board):
                return PostFactory.create()

            def test_403이_반환된다(self, subject):
                assert subject.status_code == 403

            class Context_로그인_사용자가_마스터일경우:

                @pytest.fixture
                def logged_in_user(self):
                    return MasterUserFactory.create()

                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_게시글이_삭제된다(self, subject, post):
                    assert post.is_deleted == False
                    post.reload()
                    assert post.is_deleted == True

    class Describe_like_post:

        @pytest.fixture(autouse=True)
        def subject(self, client, headers, post):
            url = url_for('PostView:like_post', board_id=post.board.id, post_id=post.id)
            return client.post(url, headers=headers)

        class Context_정상요청:

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_post에_like한_user가_추가된다(self, subject, post, logged_in_user):
                assert len(post.likes) == 0
                post.reload()
                assert str(logged_in_user.id) in post.likes
                assert len(post.likes) == 1

        class Context_비로그인_사용자가_게시글을_like할경우:

            @pytest.fixture
            def post(self, board):
                return PostFactory.create(board=board.id)

            @pytest.fixture
            def logged_in_user(self):
                return None

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
                assert subject.json['message'] == '로그인하지 않은 사용자입니다.'

            def test_좋아요가_반영되지_않는다(self, subject, post):
                post.reload()
                assert len(post.likes) == 0

            class Context_유효하지_않은_토큰으로_like할경우:

                @pytest.fixture
                def token(self):
                    return uuid.uuid4()

                def test_401이_반환된다(self, subject):
                    assert subject.status_code == 401
                    assert subject.json['message'] == '유효하지 않은 토큰입니다'

                def test_좋아요가_반영되지_않는다(self, subject, post):
                    post.reload()
                    assert len(post.likes) == 0

        class Context_로그인_유저가_이미_like한경우:
            @pytest.fixture
            def post(self, logged_in_user, board):
                return PostFactory.create(board=board.id, likes=[str(logged_in_user.id)])

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_좋아요_개수가_변하지_않는다(self, subject, post, logged_in_user):
                assert str(logged_in_user.id) in post.likes
                assert len(post.likes) == 1
                post.reload()
                assert len(post.likes) == 1

    class Describe_cancel_like:

        @pytest.fixture
        def post(self, board, logged_in_user):
            return PostFactory.create(board=board.id, likes=[str(logged_in_user.id)])

        @pytest.fixture(autouse=True)
        def subject(self, client, headers, post):
            url = url_for('PostView:cancel_like_post', board_id=post.board.id, post_id=post.id)
            return client.post(url, headers=headers)

        class Context_정상요청:

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_post에_like한_user가_삭제된다(self, subject, post):
                assert len(post.likes) == 1
                post.reload()
                assert len(post.likes) == 0

        class Context_비로그인_사용자가_게시글_like를_취소하는경우:

            @pytest.fixture
            def post(self, board):
                return PostFactory.create(board=board.id)

            @pytest.fixture
            def logged_in_user(self):
                return None

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
                assert subject.json['message'] == '로그인하지 않은 사용자입니다.'

            class Context_유효하지_않은_토큰으로_게시글_like를_취소할경우:

                @pytest.fixture
                def token(self):
                    return uuid.uuid4()

                def test_401이_반환된다(self, subject):
                        assert subject.status_code == 401
                        assert subject.json['message'] == '유효하지 않은 토큰입니다'

        class Context_로그인_사용자의_like가_없던경우:

            @pytest.fixture
            def post(self, board):
                return PostFactory.create(board=board.id)

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_좋아요_개수가_변하지_않는다(self, subject, post):
                assert len(post.likes) == 0
                post.reload()
                assert len(post.likes) == 0
