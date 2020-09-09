import jwt
import pytest
import factory

from flask import url_for, current_app
from bson.json_util import dumps as bson_dumps
from json import dumps as json_dumps

from app.models import Post
from tests.factories.post import PostFactory, DeletedPostFactory
from tests.factories.user import UserFactory, MasterUserFactory
from tests.factories.board import BoardFactory, DeletedBoardFactory


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

        @pytest.fixture
        def headers(self, logged_in_user):
            token = jwt.encode({"user_id": bson_dumps(logged_in_user.id),
                                "is_master": logged_in_user.master_role},
                               current_app.config['SECRET'],
                               current_app.config['ALGORITHM'])
            headers = {
                'Authorization': token
            }
            return headers

        class Describe_post:

            @pytest.fixture
            def form(self):
                return {
                    "title" : factory.Faker('sentence').generate(),
                    "content" : factory.Faker('sentence').generate(),
                    "tags" : ["tags"]
                }

            @pytest.fixture(autouse=True)
            def subject(self, client, form, headers, board):
                url = url_for('PostView:post', board_id=board.id)
                return client.post(url, headers = headers, data=json_dumps(form))

            class Context_정상요청:
                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_게시글이_추가된다(self, subject):
                    assert Post.objects.count() == 1

                def test_추가된_게시글과_요청이_동일하다(self, form, logged_in_user, subject):
                    post = Post.objects.first()
                    assert post.title == form['title']
                    assert post.content == form['content']
                    assert post.tags == form['tags']
                    assert post.author.id == logged_in_user.id

            class Context_요청이_유효하지_않은경우:

                @pytest.fixture
                def form(self):
                    return {
                        "content": factory.Faker('sentence').generate(),
                        "tags": ["tags"]
                    }

                def test_422가_반환된다(self, subject):
                    assert subject.status_code == 422

                def test_게시글이_저장되지_않는다(self, subject):
                    post = Post.objects.first()
                    assert post is None

                class Context_요청_type이_유효하지_않은경우:
                    @pytest.fixture
                    def form(self):
                        return {
                            "title": factory.Faker('sentence').generate(),
                            "content": factory.Faker('sentence').generate(),
                            "tags": "tags"
                        }

                    def test_422가_반환된다(self, subject):
                        assert subject.status_code == 422

                    def test_게시글이_저장되지_않는다(self, subject):
                        post = Post.objects.first()
                        assert post is None

            class Context_없는_게시판에_게시글을_생성하는_경우:
                @pytest.fixture
                def board(self):
                    return DeletedBoardFactory.create()

                def test_404가_반환된다(self, subject):
                    assert subject.status_code == 404

                def test_게시글이_저장되지_않는다(self, subject):
                    post = Post.objects.first()
                    assert post is None

            class Context_비로그인_사용자가_게시글을_생성하는경우:

                @pytest.fixture(autouse=True)
                def subject(self, client, form, board):
                    url = url_for('PostView:post', board_id=board.id)
                    return client.post(url, data=json_dumps(form))

                def test_401이_반환된다(self, subject):
                    assert subject.status_code == 401

                def test_게시글이_저장되지_않는다(self, subject):
                    post = Post.objects.first()
                    assert post is None

        class Describe_get:

            @pytest.fixture(autouse=True)
            def subject(self, client, post):
                url = url_for('PostView:get', board_id=post.board.id, post_id=post.id)
                return client.get(url)

            class Context_정상요청:
                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_조회한_게시글이_요청과_동일하다(self, subject, post):
                    assert subject.json['title'] == post.title
                    assert subject.json['content'] == post.content
                    assert subject.json['tags'] == post.tags

            class Context_없는_게시판_게시글을_요청하는_경우:
                @pytest.fixture
                def board(self):
                    return DeletedBoardFactory.create()

                def test_404가_반환된다(self, subject):
                    assert subject.status_code == 404

        class Describe_update:

            @pytest.fixture
            def form(self):
                return {
                    "tags": ["updated_tag"]
                }

            @pytest.fixture(autouse=True)
            def subject(self, client, form, headers, post):
                url = url_for('PostView:update', board_id=post.board.id, post_id=post.id)
                return client.put(url, headers=headers, data=json_dumps(form))

            class Context_정상요청:
                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_게시글이_수정된다(self, form, subject):
                    post = Post.objects.first()
                    assert post.tags == form['tags']

            class Context_없는_게시글을_수정하는_경우:
                @pytest.fixture
                def post(self, board):
                    return DeletedPostFactory.create(board=board.id)

                def test_404가_반환된다(self, subject):
                    assert subject.status_code == 404

                def test_게시글이_수정되지_않는다(self, form, subject):
                    post = Post.objects.first()
                    assert post.tags != form['tags']

            class Context_비로그인_사용자가_게시글을_수정하는경우:

                @pytest.fixture(autouse=True)
                def subject(self, client, form, post):
                    url = url_for('PostView:update', board_id=post.board.id, post_id=post.id)
                    return client.put(url, data=json_dumps(form))

                def test_401이_반환된다(self, subject):
                    assert subject.status_code == 401

                def test_게시글이_수정되지_않는다(self, form, subject):
                    post = Post.objects.first()
                    assert post.tags != form['tags']

            class Context_로그인_사용자가_게시글_작성자가_아닌경우:

                @pytest.fixture
                def post(self, board):
                    return PostFactory.create(board=board.id)

                def test_403이_반환된다(self, subject):
                    assert subject.status_code == 403

                def test_게시글이_수정되지_않는다(self, form, subject):
                    post = Post.objects.first()
                    assert post.tags != form['tags']

                class Context_로그인_사용자가_마스터일경우:

                    @pytest.fixture
                    def logged_in_user(self):
                        return MasterUserFactory.create()

                    def test_200이_반환된다(self, subject):
                        assert subject.status_code == 200

                    def test_게시글이_수정된다(self, form, subject):
                        post = Post.objects.first()
                        assert post.tags == form['tags']

            class Context_Client의_요청이_유효하지_않은경우:
                    @pytest.fixture
                    def form(self):
                        return {
                            "tag": ["tags"]
                        }

                    def test_422가_반환된다(self, subject):
                        assert subject.status_code == 422

                    def test_게시글이_수정되지_않는다(self, subject, form):
                        post = Post.objects.first()
                        assert post.tags != form['tag']

        class Describe_delete:

            @pytest.fixture(autouse=True)
            def subject(self, client, headers, post):
                url = url_for('PostView:delete', board_id=post.board.id, post_id=post.id)
                return client.delete(url, headers=headers)

            class Context_정상요청:
                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_게시글이_soft_delete된다(self, subject):
                    post = Post.objects.first()
                    assert post is not None
                    assert post.is_deleted == True

            class Context_비로그인_사용자가_게시글을_삭제하는경우:

                @pytest.fixture(autouse=True)
                def subject(self, client, post):
                    url = url_for('PostView:delete', board_id=post.board.id, post_id=post.id)
                    return client.delete(url)

                def test_401이_반환된다(self, subject):
                    assert subject.status_code == 401

                def test_게시글이_삭제되지_않는다(self, subject):
                    post = Post.objects.first()
                    assert post is not None
                    assert post.is_deleted == False

            class Context_로그인_사용자가_게시글_작성자가_아닌경우:

                @pytest.fixture
                def post(self, board):
                    return PostFactory.create(board=board.id)

                def test_403이_반환된다(self, subject):
                    assert subject.status_code == 403

                def test_게시글이_삭제되지_않는다(self, subject):
                    post = Post.objects.first()
                    assert post is not None
                    assert post.is_deleted == False

                class Context_로그인_사용자가_마스터일경우:

                    @pytest.fixture
                    def logged_in_user(self):
                        return MasterUserFactory.create()

                    def test_200이_반환된다(self, subject):
                        assert subject.status_code == 200

                    def test_게시글이_삭제된다(self, subject):
                        post = Post.objects.first()
                        assert post is not None
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
                    post.reload()
                    assert str(logged_in_user.id) in post.likes
                    assert len(post.likes) == 1

            class Context_비로그인_사용자가_게시글을_좋아하는경우:

                @pytest.fixture(autouse=True)
                def subject(self, client, post):
                    url = url_for('PostView:like_post', board_id=post.board.id, post_id=post.id)
                    return client.post(url)

                def test_401이_반환된다(self, subject):
                    assert subject.status_code == 401

                def test_게시글에_좋아요가_추가되지_않는다(self, subject, post):
                    assert len(post.likes) == 0

            class Context_이미_like한경우:
                @pytest.fixture
                def post(self, post, logged_in_user):
                    post.like(str(logged_in_user.id))
                    return post

                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_좋아요_개수가_변하지_않는다(self, subject, post, logged_in_user):
                    post.reload()
                    assert str(logged_in_user.id) in post.likes
                    assert len(post.likes) == 1

        class Describe_cancel_like:

            @pytest.fixture
            def post(self, post, logged_in_user):
                post.like(str(logged_in_user.id))
                return post

            @pytest.fixture(autouse=True)
            def subject(self, client, headers, post):
                url = url_for('PostView:cancel_like_post', board_id=post.board.id, post_id=post.id)
                return client.post(url, headers=headers)

            class Context_정상요청:

                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_post에_like한_user가_삭제된다(self, subject, post, logged_in_user):
                    post.reload()
                    assert str(logged_in_user.id) not in post.likes
                    assert len(post.likes) == 0

            class Context_비로그인_사용자가_게시글을_좋아요_취소하는경우:

                @pytest.fixture(autouse=True)
                def subject(self, client, post):
                    url = url_for('PostView:cancel_like_post', board_id=post.board.id, post_id=post.id)
                    return client.post(url)

                def test_401이_반환된다(self, subject):
                    assert subject.status_code == 401

                def test_게시글에_좋아요가_삭제되지_않는다(self, subject, post):
                    post.reload()
                    assert len(post.likes) == 1

            class Context_기존에_like가_없던경우:
                @pytest.fixture
                def post(self, post, logged_in_user):
                    post.cancel_like(str(logged_in_user.id))
                    return post

                def test_200이_반환된다(self, subject):
                    assert subject.status_code == 200

                def test_좋아요_개수가_변하지_않는다(self, subject, post, logged_in_user):
                    post.reload()
                    assert str(logged_in_user.id) not in post.likes
                    assert len(post.likes) == 0