from json import dumps

import factory
import jwt
import pytest
from flask import current_app, url_for

from tests.factories.post import PostFactory
from tests.factories.user import UserFactory, MasterUserFactory
from tests.factories.comment import CommentFactory, DeletedCommentFactory, ReplyFactory
from app.models import Comment


class Describe_CommentView:
    @pytest.fixture
    def post(self):
        return PostFactory.create()

    @pytest.fixture
    def logged_in_user(self):
        return UserFactory.create()

    @pytest.fixture
    def headers(self, logged_in_user):
        token = jwt.encode({"user_id": dumps(str(logged_in_user.id)),
                            "is_master": logged_in_user.master_role}, current_app.config['SECRET'],
                           current_app.config['ALGORITHM'])
        headers = {
            'Authorization': token
        }
        return headers

    class Describe_index:
        @pytest.fixture
        def subject(self, client, headers, post):
            url = url_for('CommentView:index', board_id=post.board.id, post_id=post.id)
            return client.get(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_빈_list가_반환된다(self, subject):
            body = subject.json

            assert body['total'] == 0
            assert body['items'] == []


    class Describe_post:
        @pytest.fixture
        def form(self):
            return {'content': factory.Faker('sentence').generate()}

        @pytest.fixture
        def subject(self, client, headers, post, form):
            url = url_for('CommentView:post', board_id=post.board.id, post_id=post.id)
            return client.post(url, headers=headers, data=dumps(form))

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_comment_갯수가_증가한다(self, subject):
            total_comment_count = Comment.objects().count()
            assert total_comment_count == 1

        def test_comment가_입력값과_동일하다(self, subject, form):
            content = Comment.objects().get().content
            assert content == form['content']

        class Context_content가_입력되지_않은경우:
            @pytest.fixture
            def form(self):
                return {'content': ''}

            def test_422가_반환된다(self, subject):
                assert subject.status_code == 422

        class Context_user가_로그인_하지_않은경우:
            @pytest.fixture
            def headers(self):
                headers = {
                    'Authorization': None
                }
                return headers

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401


    class Describe_update:
        @pytest.fixture
        def form(self):
            return {'content': factory.Faker('sentence').generate()}

        @pytest.fixture
        def comment(self, post, logged_in_user):
            return CommentFactory.create(post=post, author=logged_in_user)

        @pytest.fixture
        def subject(self, client, headers, post, comment, form):
            url = url_for('CommentView:update', board_id=post.board.id, post_id=post.id, comment_id=comment.id)
            return client.put(url, headers=headers, data=dumps(form))

        def test_200이반환된다(self, subject):
            assert subject.status_code == 200

        def test_content_내용이_변경된다(self, subject, form):
            content = Comment.objects().get().content
            assert content == form['content']

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

        class Context_content가_입력되지_않은경우:
            @pytest.fixture
            def form(self):
                return {'content': ''}

            def test_422가_반환된다(self, subject):
                assert subject.status_code == 422

        class Context_이미_삭제된_comment를_수정하는경우:
            @pytest.fixture
            def comment(self, post):
                return DeletedCommentFactory.create(post=post)

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404

        class Context_user가_로그인_하지_않은경우:
            @pytest.fixture
            def headers(self):
                headers = {
                    'Authorization': None
                }
                return headers

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401


    class Describe_delete:
        @pytest.fixture
        def comment(self, post, logged_in_user):
            return CommentFactory.create(post=post, author=logged_in_user)

        @pytest.fixture
        def subject(self, client, headers, post, comment):
            url = url_for('CommentView:delete', board_id=post.board.id, post_id=post.id, comment_id=comment.id)
            return client.delete(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_comment의_is_deleted가_True가_된다(self, subject):
            comment_is_deleted = Comment.objects().get().is_deleted
            assert comment_is_deleted is True

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
                    return subject.status_code == 200

                def test_comment의_is_delete가_True가_된다(self, subject):
                    comment_is_deleted = Comment.objects().get().is_deleted
                    assert comment_is_deleted is True

        class Context_이미_삭제된_comment를_삭제하는경우:
            @pytest.fixture
            def comment(self, post):
                return DeletedCommentFactory.create(post=post)

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404

        class Context_user가_로그인_하지_않은경우:
            @pytest.fixture
            def headers(self):
                headers = {
                    'Authorization': None
                }
                return headers

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401


    class Describe_like_comment:
        @pytest.fixture
        def comment(self, post):
            return CommentFactory.create(post=post)

        @pytest.fixture
        def subject(self, client, headers, post, comment):
            url = url_for('CommentView:like_comment', board_id=post.board.id, post_id=post.id, comment_id=comment.id)
            return client.post(url, headers=headers)

        def test_200이_반환된다(self, subject):
            return subject.status_code == 200

        def test_좋아요_갯수가_증가한다(self, subject):
            total_like_count = len(Comment.objects().get().likes)
            assert total_like_count == 1

        def test_좋아요한_사람이_logged_in_user와_같다(self, subject, logged_in_user):
            comment_liked_user = Comment.objects().get().likes[0]
            assert comment_liked_user == str(logged_in_user.id)

        class Context_사용자가_이미_좋아요를_누른경우:
            @pytest.fixture
            def comment(self, post, logged_in_user):
                return CommentFactory.create(post=post, likes=[str(logged_in_user.id)])

            def test_200이_반환된다(self, subject):
                return subject.status_code == 200

            def test_좋아요_갯수가_유지된다(self, subject):
                total_like_count = len(Comment.objects().get().likes)
                assert total_like_count == 1

            def test_좋아요한_사람이_logged_in_user와_같다(self, subject, logged_in_user):
                comment_liked_user = Comment.objects().get().likes[0]
                assert comment_liked_user == str(logged_in_user.id)

        class Context_이미_삭제된_comment에_좋아요하는경우:
            @pytest.fixture
            def comment(self, post):
                return DeletedCommentFactory.create(post=post)

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404

        class Context_user가_로그인_하지_않은경우:
            @pytest.fixture
            def headers(self):
                headers = {
                    'Authorization': None
                }
                return headers

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401


    class Describe_cancel_like_comment:
        @pytest.fixture
        def comment(self, post, logged_in_user):
            return CommentFactory.create(post=post, likes=[str(logged_in_user.id)])

        @pytest.fixture
        def subject(self, client, headers, post, comment):
            url = url_for('CommentView:cancel_like_comment', board_id=post.board.id, post_id=post.id, comment_id=comment.id)
            return client.post(url, headers=headers)

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test__좋아요_갯수가_감소한다(self, subject):
            total_like_count = len(Comment.objects().get().likes)
            assert total_like_count == 0

        class Context_사용자가_좋아요를_누르지_않았던_경우:
            @pytest.fixture
            def comment(self, post):
                return CommentFactory.create(post=post)

            def test_200이_반환된다(self, subject):
                assert subject.status_code == 200

            def test_좋아요_갯수가_유지된다(self, subject):
                total_like_count = len(Comment.objects().get().likes)
                assert total_like_count == 0

        class Context_이미_삭제된_comment에_좋아요_취소하는경우:
            @pytest.fixture
            def comment(self, post):
                return DeletedCommentFactory.create(post=post)

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404

        class Context_user가_로그인_하지_않은경우:
            @pytest.fixture
            def headers(self):
                headers = {
                    'Authorization': None
                }
                return headers

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401


    class Describe_post_reply:
        @pytest.fixture
        def comment(self, post):
            return CommentFactory.create(post=post)

        @pytest.fixture
        def form(self):
            return {'content': factory.Faker('sentence').generate()}

        @pytest.fixture
        def subject(self, client, headers, post, comment, form):
            url = url_for('CommentView:post_reply', board_id=post.board.id, post_id=post.id, comment_id=comment.id)
            return client.post(url, headers=headers, data=dumps(form))

        def test_200이_반환된다(self, subject):
            assert subject.status_code == 200

        def test_comment_갯수가_증가한다(self, subject):
            total_comment_count = Comment.objects().count()
            assert total_comment_count == 2

        def test_comment가_입력값과_동일하다(self, subject, form):
            content = Comment.objects()[1].content
            assert content == form['content']

        class Context_대댓글에_댓글을_다는경우:
            @pytest.fixture
            def comment(self, post):
                return ReplyFactory.create(post=post)

            def test_400이_반환된다(self, subject):
                assert subject.status_code == 400

        class Context_content가_입력되지_않은경우:
            @pytest.fixture
            def form(self):
                return {'content': ''}

            def test_422가_반환된다(self, subject):
                assert subject.status_code == 422

        class Context_이미_삭제된_comment에_대댓글을_다는경우:
            @pytest.fixture
            def comment(self, post):
                return DeletedCommentFactory.create(post=post)

            def test_404가_반환된다(self, subject):
                assert subject.status_code == 404

        class Context_user가_로그인_하지_않은경우:
            @pytest.fixture
            def headers(self):
                headers = {
                    'Authorization': None
                }
                return headers

            def test_401이_반환된다(self, subject):
                assert subject.status_code == 401
