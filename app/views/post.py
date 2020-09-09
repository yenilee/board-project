import json

from flask_classful import FlaskView, route
from flask import g, request, jsonify
from bson import ObjectId
from marshmallow import ValidationError

from app.utils import login_required, check_board, check_post
from app.models import Post
from app.serializers.post import PostCreateSchema, PostDetailSchema, PostUpdateSchema


class PostView(FlaskView):

    @route('', methods=['POST'])
    @login_required
    @check_board
    def post(self, board_id):

        """
        게시글 생성 API
        :param board_id: 게시판 objectID
        :return: message
        """
        try:
            post = PostCreateSchema().load(json.loads(request.data))

            post.author = g.user_id
            post.board = ObjectId(board_id)
            post.save()

            return '', 200

        except ValidationError as err:
            return err.messages, 422


    @route('/<post_id>', methods=['GET'])
    @check_board
    @check_post
    def get(self, board_id, post_id):
        """
        게시글 조회 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: 게시글
        """
        schema = PostDetailSchema()
        post = Post.objects(board=board_id, id=post_id).get()
        return schema.dump(post), 200

    @route('/<post_id>', methods=['PUT'])
    @login_required
    @check_board
    @check_post
    def update(self, board_id, post_id):
        """
        게시글 수정 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: message
        """
        try:
            post = Post.objects(id=post_id, board=board_id).get()

            if not post.user_auth_check(g.user_id, g.master_role):
                return jsonify(message='권한이 없는 사용자입니다'), 403

            data = PostUpdateSchema().load(json.loads(request.data))
            post.update(**data)
            return '', 200

        except ValidationError as err:
            return err.messages, 422


    @route('/<post_id>', methods=['DELETE'])
    @login_required
    @check_board
    @check_post
    def delete(self, board_id, post_id):
        """
        게시글 삭제 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: message
        """
        post = Post.objects(board=board_id, id=post_id).get()
        if not post.user_auth_check(g.user_id, g.master_role):
            return jsonify(message='권한이 없는 사용자입니다'), 403

        post.soft_delete()
        return '', 200


    @route('/<post_id>/like', methods=['POST'])
    @login_required
    @check_board
    @check_post
    def like_post(self, board_id, post_id):
        """
        게시글 좋아요 기능 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: message
        """
        post = Post.objects(board=board_id, id=post_id).get()
        post.like(g.user_id)
        return '', 200

    @route('/<post_id>/cancel-like', methods=['POST'])
    @login_required
    @check_board
    @check_post
    def cancel_like_post(self, board_id, post_id):
        """
        게시글 좋아요 기능 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: message
        """
        post = Post.objects(board=board_id, id=post_id).get()
        post.cancel_like(g.user_id)
        return '', 200
