import json

from app.models import Board
from flask_classful import FlaskView, route
from flask import jsonify, request

class BoardView(FlaskView):
    # 게시판 목록
    @route('/', methods=['GET'])
    def list_board(self):

        board_list = Board.objects(is_deleted = True)

        board_data = [
            {"name": board.name}
        for board in board_list]

        return jsonify(data=board_data), 200