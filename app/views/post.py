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