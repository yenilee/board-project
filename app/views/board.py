import json

from app.models import Board, User, Post
from flask_classful import FlaskView, route
from flask import jsonify, request, g
from app.utils import auth


class BoardView(FlaskView):
    # 게시판 카테고리
    @route('/category', methods=['GET'])
    def get_board_category(self):
        board_data = Board.objects(is_deleted=False)

        board_category = [
            {"name": board.name}
            for board in board_data]

        return jsonify(data=board_category), 200


    # 게시판 생성
    @route('', methods=['POST'])
    @auth
    def post(self):
        name = json.loads(request.data)['name']

        # 유저의 권한 확인
        if g.auth == False:
            return jsonify(message='권한이 없습니다.'), 403

        # 현재 존재하는 board와 이름 중복 확인
        if Board.objects(name=name, is_deleted=False):
            return jsonify(message='이미 등록된 게시판입니다.'), 400

        board = Board(name=name)
        board.save()

        return '', 200


    # 게시판 목록 조회
    @route('/<board_name>', methods=['GET'])
    def list_board(self, board_name):
        page = request.args.get('page', 1, int)

        # pagination
        limit = 10
        skip = (page - 1) * limit

        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        post_list = Post.objects(board=board_id, is_deleted=False)
        post_data=[
            {"total": len(post_list),
             "posts": [{"number": n,
                        "post_id": post.post_id,
                        "title": post.title,
                        "content": post.content,
                        "created_at": post.created_at,
                        "likes": len(post.likes),
                        "is_deleted":post.is_deleted}
                    for n, post in zip(range(len(post_list) - skip, 0, -1), post_list[skip:skip + limit])]}]
        return jsonify(data=post_data), 200

    # @route('/<board_name>', methods=['DELETE'])
    # @auth
    # def delete(self, board_name):
    #     if not g.auth:
    #         jsonify(message='권한이 없는 사용자입니다.'), 403
