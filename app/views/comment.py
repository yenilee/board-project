from flask import g
from flask_apispec import use_kwargs
from flask_classful import FlaskView, route

from app.models import Comment
from app.serializers.comment import CommentCreateSchema, CommentUpdateSchema, PaginatedCommentsSchema
from app.utils import check_board, check_comment, check_post, login_required


class CommentView(FlaskView):
    @check_board
    @check_post
    def index(self, board_id, post_id):
        """
        게시글 댓 조회 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: 게시글(작성자, 제목, 내용, 좋아요, 태그)
        """
        # comments = Comment.objects(post=g.post.id)
        # schema = CommentGetSchema(many=True)

        result = Comment.objects(post=g.post.id).paginate(page=1, per_page=10)

        # result = {
        #     'total':0,
        #     'items':[]
        # }

        dumps = PaginatedCommentsSchema().dump(result)

        return dumps, 200


    @route('', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @use_kwargs(CommentCreateSchema)
    def post(self, board_id, post_id, **kwargs):
        """
        댓글 생성 API
        작성자: avery
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :return: message
        """
        comment = Comment(
            post=g.post.id,
            author=g.user,
            content=kwargs['content'],
        )
        comment.save()
        return '', 200

    @route('<comment_id>', methods=['PUT'])
    @login_required
    @check_board
    @check_post
    @check_comment
    @use_kwargs(CommentUpdateSchema)
    def update(self, board_id, post_id, comment_id, **kwargs):
        """
        댓글 수정 API
        작성자: avery
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :param comment_id: 댓글 objectId
        :return: message
        """
        comment = Comment.objects(id=comment_id).get()
        result = comment.update_comment(g.user, g.auth, **kwargs)
        if result is False:
            return {'message': '권한이 없습니다.'}, 403
        return '', 200


    @route('<comment_id>', methods=['DELETE'])
    @login_required
    @check_board
    @check_post
    @check_comment
    def delete(self, board_id, post_id, comment_id):
        """
        댓글 삭제 API
        작성자: avery
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :param comment_id: 댓글 objectId
        :return: message
        """
        comment = Comment.objects(id=comment_id).get()
        result = comment.soft_delete_comment(g.user, g.auth)
        if result is False:
            return {'message': '권한이 없습니다.'}, 403
        return '', 200


    @route('/<comment_id>/like', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @check_comment
    def like_comment(self, board_id, post_id, comment_id):
        """
        댓글 좋아요 기능 API
        작성자: dana
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :param comment_id: 댓글 objectId
        :return: message
        """
        status = Comment.find_user_in_list(comment_id, g.user)
        comment = Comment.objects(id=comment_id).get()
        comment.like(status, g.user)
        return {'message': '좋아요가 반영되었습니다.'}, 200


    @route('/<comment_id>/cancel-like', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @check_comment
    def cancel_like_comment(self, board_id, post_id, comment_id):
        """
        댓글 좋아요 취소 기능 API
        작성자: dana
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :param comment_id: 댓글 objectId
        :return: message
        """
        status = Comment.find_user_in_list(comment_id, g.user)
        comment = Comment.objects(id=comment_id).get()
        comment.cancel_like(status, g.user)
        return {'message': '좋아요가 취소되었습니다.'}, 200


    @route('/<comment_id>/replies', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @check_comment
    @use_kwargs(CommentCreateSchema)
    def post_reply(self, board_id, post_id, comment_id, **kwargs):
        """
        대댓글 생성 기능 API
        작성자: dana
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :param comment_id: 댓글 objectId
        :return: message
        """
        if g.comment.is_replied:
            return {'message': '답글을 달 수 없는 댓글입니다.'}, 400

        reply = Comment(
            post=g.post.id,
            author=g.user,
            reply=g.comment.id,
            content=kwargs['content'],
            is_replied=True
        )
        reply.save()

        return '', 200