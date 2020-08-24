import json

from app.models import Board, Post
from flask_classful import FlaskView, route
from flask import jsonify, request, g
from app.utils import auth


class PostView(FlaskView):

    # 게시글 작성 API
    @route('', methods=['POST'])
    @auth
    def create_post(self, board_name):
        data = json.loads(request.data)

        for board in Board.objects(name=board_name):
            post = Post(
                board   = board.id,
                author  = g.user,
                title   = data['title'],
                content = data['content'],
                post_id = Post.objects.count()+1
            ).save()

        return '', 200


    # 게시글 읽기
    @route('/<int:post_id>', methods=['GET'])
    def get_post(self, board_name, post_id):

        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400

        try:
            post = Post.objects(post_id=post_id, is_deleted=False).get()
            return jsonify(post.to_json()), 200
        except:
            return jsonify(message='없는 게시물입니다.'), 400


    # 게시글 삭제
    @route('/<int:post_id>', methods=['DELETE'])
    @auth
    def delte_post(self, board_name, post_id):
        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False)
        # 게시글 존재 여부 확인
        if not post:
            return jsonify(message='잘못된 주소입니다.'), 400

        # 삭제 가능 user 확인
        if g.user == post.get().author.id or g.auth == True:
            post.update(is_deleted=True)
            return jsonify(message='삭제되었습니다.'), 200
        return jsonify(message='권한이 없습니다.'), 403