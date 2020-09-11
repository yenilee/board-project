import enum
import json

from flask import g, request
from flask_classful import FlaskView, route
from bson import ObjectId

from app.models import Comment
from app.serializers.comment import CommentCreateSchema, CommentUpdateSchema, PaginatedCommentsSchema, CommentListWithReplySchema
from app.utils import check_board, check_comment, check_post, login_required, comment_update_validator, comment_create_validator


# 최신순, 과거순, 순공감순
class CommentSearchOrder(enum.Enum):
    recent = 'recent'
    pure_like = 'pure_like'


class CommentView(FlaskView):
    @check_board
    @check_post
    def index(self, board_id, post_id, page=1):
        """
        게시글 댓 조회 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :param page: 페이지 번호
        :return: 게시글(작성자, 제목, 내용, 좋아요, 태그)
        """
        if request.args:
            page = int(request.args.get('page'))

        result = Comment.objects(post=post_id).order_by('-created_at')
        comments = CommentListWithReplySchema(many=True).dump(result)

        return {"comments" : comments}, 200


    @route('', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @comment_create_validator
    def post(self, board_id, post_id):
        """
        댓글 생성 API
        작성자: avery
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :return: message
        """
        comment = CommentCreateSchema().load(json.loads(request.data))
        comment.author = ObjectId(g.user_id)
        comment.post = ObjectId(post_id)
        comment.save()
        return '', 200

    @route('<comment_id>', methods=['PUT'])
    @login_required
    @check_board
    @check_post
    @check_comment
    @comment_update_validator
    def update(self, board_id, post_id, comment_id):
        """
        댓글 수정 API
        작성자: avery
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :param comment_id: 댓글 objectId
        :return: message
        """
        comment = Comment.objects(id=comment_id).get()
        data = CommentUpdateSchema().load(json.loads(request.data))

        # permission check
        if comment.author.id != ObjectId(g.user_id) and g.master_role is False:
            return {'message': '권한이 없습니다.'}, 403

        comment.update(**data)
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

        # permission check
        if comment.author.id != ObjectId(g.user_id) and g.master_role is False:
            return {'message': '권한이 없습니다.'}, 403

        comment.soft_delete(g.user_id, g.master_role)
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
        comment = Comment.objects(id=comment_id).get()
        comment.like(g.user_id)
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
        comment = Comment.objects(id=comment_id).get()
        comment.cancel_like(g.user_id)
        return {'message': '좋아요가 취소되었습니다.'}, 200


    @route('/<comment_id>/replies', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @check_comment
    @comment_create_validator
    def post_reply(self, board_id, post_id, comment_id):
        """
        대댓글 생성 기능 API
        작성자: dana
        :param board_id: 게시판 objectId
        :param post_id: 게시글 objectId
        :param comment_id: 댓글 objectId
        :return: message
        """
        if Comment.objects(id=comment_id).get().is_reply:
            return {'message': '답글을 달 수 없는 댓글입니다.'}, 400

        reply = CommentCreateSchema().load(json.loads(request.data))
        reply.author = ObjectId(g.user_id)
        reply.post = ObjectId(post_id)
        reply.reply = ObjectId(comment_id)
        reply.is_reply = True
        reply.save()

        return '', 200