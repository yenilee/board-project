import json

from flask_classful import FlaskView, route
from flask import jsonify, request, g
from flask_apispec import use_kwargs

from app.utils import login_required, check_board, check_post, post_validator, pagination
from app.models import Post, Comment
from app.serializers.post import PostGetSchema, PostSchema


class PostView(FlaskView):

    @route('', methods=['POST'])
    @login_required
    @check_board
    @post_validator
    def post(self, board_id):
        """
        게시글 생성 API
        작성자: avery
        :param board_id: 게시판 objectID
        :return: message
        """
        post = json.loads(request.data)
        schema = PostSchema()
        schema.load(post).save()

        return jsonify(message='게시글이 등록되었습니다.'), 200


    @route('/<post_id>', methods=['GET'])
    @check_board
    @check_post
    def get(self, board_id, post_id):
        """
        게시글 조회 API
        작성자: avery
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: 게시글(작성자, 제목, 내용, 좋아요, 태그)
        """
        schema = PostGetSchema()
        post = Post.objects.get(id=post_id)

        return schema.dump(post), 200


    @route('/<post_id>', methods=['DELETE'])
    @login_required
    @check_board
    @check_post
    def delete(self, board_id, post_id):
        """
        게시글 삭제 API
        작성자: dana
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: message
        """
        if g.user == g.post.author.id or g.auth == True:
            post.delete()
            g.post.update(is_deleted=True)
            return jsonify(message='삭제되었습니다.'), 200
        return jsonify(message='권한이 없습니다.'), 403


    @route('/<post_id>', methods=['PUT'])
    @login_required
    @check_board
    @check_post
    @post_validator
    def update(self, board_id, post_id):
        """
        게시글 수정 API
        작성자: dana
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: message
        """
        data = json.loads(request.data)
        tags = data.get('tags')

        # 수정 가능 user 확인
        if g.user == g.post.author.id or g.auth == True:
            g.post.update(
                title = data['title'],
                content = data['content'],
                tags = tags
            )
            return jsonify(message='수정되었습니다.'), 200
        return jsonify(message='권한이 없습니다.'), 403


    @route('/<post_id>/likes', methods=['POST'])
    @login_required
    @check_board
    @check_post
    def like_post(self, board_id, post_id):
        """
        게시글 좋아요 기능 API
        작성자: dana
        :param board_id: 게시판 objectID
        :param post_id: 게시글 objectID
        :return: message
        """

        post_id = request.get('post_id')

        # View
        # - http protocol로부터 인자를 획득
        #
        # - response로 결과를 반환

        post = Post.objects(id=g.post.id)
        post.like(g.user)

        return '', 200
        # # 좋아요 등록
        # if not post:
        #     g.post.update(push__likes=g.user)
        #     return jsonify(message="'내가 좋아요한 게시글'에 등록되었습니다.'"), 200
        #
        # # 좋아요 취소
        # g.post.update(pull__likes=g.user)
        # return jsonify(message="'내가 좋아요한 게시글'에서 삭제되었습니다.'"), 200