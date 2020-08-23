import json

from app.models     import Board, Post
from flask_classful import FlaskView, route
from flask          import jsonify, request, g
from app.utils      import auth


class BoardView(FlaskView):
    # 게시판 이름 목록
    @route('/', methods=['GET'])
    def get_board_menu(self):

        board_data = Board.objects(is_deleted = True)

        board_menu = [
            {"name": board.name}
        for board in board_data]

        return jsonify(data=board_menu), 200


    # 게시판 생성
    @route('', methods=['POST'])
    def post(self):

        name = json.loads(request.data)['name']

        # 현재 존재하는 board와 이름 중복 인
        if Board.objects(name=name, is_deleted=False):
            return jsonify(message='이미 등록된 게시판입니다.'), 409

        board = Board(name=name)
        board.save()

        return '', 200


    # 게시글 작성 API
    @route('/post', methods=['POST'])
    @auth
    def create_post(self):
        data = json.loads(request.data)

        board = Board.objects(name=data['board_name']).get()
        post = Post(
            author     = g.user,
            title      = data['title'],
            content    = data['content'],
            post_id    = len(board.post)+1
        )
        board.post.append(post)
        board.save()

        return '', 200


    # 게시글 읽기
    @route('/<board_name>/<int:post_id>', methods=['GET'])
    def get_post(self, board_name, post_id):

        if not Board.objects(name=board_name):
            return jsonify(message='없는 게시판입니다.'), 400

        post = Board.objects(name=board_name).get().post[post_id-1]
        return jsonify(post.to_json()), 200




