from flask_classful import FlaskView, route
from flask import jsonify, g
from flask_apispec import use_kwargs, marshal_with

from app.utils import login_required, check_board, check_post, post_validator, post_update_validator
from app.models import Post
from app.serializers.post import PostGetSchema, PostSchema


class PostView(FlaskView):

    @route('', methods=['POST'])
    @use_kwargs(PostGetSchema, locations=['json'])
    @login_required
    @check_board
    @post_validator
    def post(self, board_id, **post):
        """
        게시글 생성 API
        :param board_id: 게시판 objectID
        :return: message
        """
        schema = PostSchema()
        schema.load(post).save()

        return '', 200


    @route('/<post_id>', methods=['GET'])
    @check_board
    @check_post
    def get(self, board_id, post_id):
        """
        게시글 조회 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: 게시글(작성자, 제목, 내용, 좋아요, 태그)
        """
        schema = PostGetSchema()
        return schema.dump(g.post), 200


    @route('/<post_id>', methods=['PUT'])
    @login_required
    @use_kwargs(PostGetSchema, locations=['json'])
    @check_board
    @check_post
    @post_update_validator
    def update(self, board_id, post_id, **post):
        """
        게시글 수정 API
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: message
        """
        if g.user == g.post.author.id or g.auth == True:
            g.post.update(**post)
            return '', 200
        return {'message':'권한이 없습니다.'}, 403


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
        if not g.post.soft_delete(g.user, g.auth):
            return {'message':'권한이 없습니다.'}, 403
        return '', 200


    @route('/<post_id>/likes', methods=['POST'])
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
        g.post.like(g.user)
        return '', 200
