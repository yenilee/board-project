import json

from app.models import Board
from flask_classful import FlaskView, route
from flask import jsonify, request

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