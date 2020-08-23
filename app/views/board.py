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