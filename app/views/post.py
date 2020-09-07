import json

from flask_classful import FlaskView, route
from flask import g, request
from flask_apispec import use_kwargs, marshal_with
from bson import ObjectId

from app.utils import login_required, check_board, check_post, post_validator, post_update_validator, pagination
from app.models import Comment, Post
from app.serializers.post import PostCreateSchema, PostDetailSchema
from app.serializers.comment import CommentGetSchema


class PostView(FlaskView):

    @route('', methods=['POST'])
    @login_required
    @post_validator
    @check_board
    def post(self, board_id):

        """
        게시글 생성 API
        :param board_id: 게시판 objectID (type: string)
        :return: message
        """
        data = json.loads(request.data)
        post = PostCreateSchema().load(data)

        post.author = g.user
        post.board = ObjectId(board_id)
        post.save()

        return '', 200


    @route('/<post_id>', methods=['GET'])
    @check_board
    @check_post
    def get(self, board_id, post_id):
        """
        게시글 조회 API
        :param board_id: 게시판 objectID (type: string)
        :param post_id: 게시글 objectID (type: string)
        :return: 게시글
        """
        schema = PostDetailSchema()
        post = Post.objects(board=board_id, id=post_id).get()
        return schema.dump(post), 200

    @route('/<post_id>', methods=['PUT'])
    @login_required
    @post_update_validator
    @check_board
    @check_post
    def update(self, board_id, post_id):
        """
        게시글 수정 API
        :param board_id: 게시판 objectID (type: string)
        :param post_id: 게시글 objectID (type: string)
        :return: message
        """
        data = json.loads(request.data)
        post = Post.objects(board=board_id, id=post_id).get()

        if not post.make_updates(g.user, g.auth, data):
            return {'message': '권한이 없습니다.'}, 403
        return '', 200


    @route('/<post_id>', methods=['DELETE'])
    @login_required
    @check_board
    @check_post
    def delete(self, board_id, post_id):
        """
        게시글 삭제 API
        :param board_id: 게시판 objectID (type: string)
        :param post_id: 게시글 objectID (type: string)
        :return: message
        """
        post = Post.objects(board=board_id, id=post_id).get()

        if not post.soft_delete(g.user, g.auth):
            return {'message':'권한이 없습니다.'}, 403
        return '', 200


    @route('/<post_id>/like', methods=['POST'])
    @login_required
    @check_board
    @check_post
    def like_post(self, board_id, post_id):
        """
        게시글 좋아요 기능 API
        :param board_id: 게시판 objectID (type: string)
        :param post_id: 게시글 objectID (type: string)
        :return: message
        """
        post = Post.objects(board=board_id, id=post_id).get()
        post.like(g.user)
        return '', 200
