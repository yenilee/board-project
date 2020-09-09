import json

from flask_classful import FlaskView, route
from flask import g, request, jsonify
from flask_apispec import use_kwargs, marshal_with
from bson import ObjectId
from marshmallow import ValidationError

from app.utils import login_required, check_board, check_post, post_validator, post_update_validator
from app.models import Post
from app.serializers.post import PostCreateSchema, PostDetailSchema, PostUpdateSchema


class PostView(FlaskView):

    @route('', methods=['POST'])
    @login_required
    @check_board
    def post(self, board_id):

        """
        게시글 생성 API
        :param board_id: 게시판 objectID (type: string)
        :return: message
        """
        data = json.loads(request.data)
        post = PostCreateSchema().load(data)

        post.author = g.user_id
        post.board = ObjectId(board_id)
        post.save()

        return '', 200


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
            data = json.loads(request.data)
            post = Post.objects(id=post_id, board=board_id).get()

            if post.user_auth_check(g.user_id, g.master_role):
                post.update(**PostUpdateSchema().load(data))
                return '', 200
            return jsonify(message='권한이 없는 사용자입니다'), 403

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

        if not post.soft_delete(g.user_id, g.master_role):
            return {'message':'권한이 없습니다.'}, 403
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
