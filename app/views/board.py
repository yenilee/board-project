import json

from flask_classful import FlaskView, route
from flask import jsonify, request, g
from marshmallow import ValidationError

from app.utils import login_required, check_board, board_create_validator
from app.models import Board, Post
from app.serializers.board import BoardCategorySchema, BoardCreateSchema, BoardUpdateSchema
from app.serializers.post import PaginatedPostsInBoardSchema, PaginatedPostsSchema, PostFilterSchema


class BoardView(FlaskView):
    @route('/categories', methods=['GET'])
    def get_category(self):
        """
        게시판 카테고리 조회 API
        :return: 게시판 카테고리
        """
        boards = Board.objects(is_deleted=False)
        board_category = BoardCategorySchema(many=True).dump(boards)
        return {'category': board_category}, 200

    @route('', methods=['POST'])
    @login_required
    @board_create_validator
    def post(self):
        """
        게시판 생성 API
        :return: message
        """
        board = BoardCreateSchema().load(json.loads(request.data))

        # Permission Check
        if g.master_role is False:
            return {'message': '권한이 없는 사용자입니다.'}, 403

        if board is False:
            return {'message': '이미 등록된 게시판입니다.'}, 409

        board.save()
        return '', 200


    @route('/<board_id>', methods=['GET'])
    @check_board
    def get(self, board_id, page=1):
        """
        게시판 글 조회 API
        :param board_id: 게시판 objectId
        :return: 게시판 글 목록 (제목, 내용, 작성자 등)
        """
        if request.args:
            page = int(request.args.get('page'))

        posts = Post.objects(board=board_id, is_deleted=False).order_by('-created_at').paginate(page=page, per_page=10)
        post_list = PaginatedPostsInBoardSchema().dump(posts)
        return post_list, 200


    @route('/<board_id>', methods=['PUT'])
    @login_required
    @check_board
    def update(self, board_id):
        """
        게시판 이름 수정 API
        :param board_id: 게시판 objectId
        :return: message
        """
        try:
            if not g.master_role:
                return jsonify(message='권한이 없는 사용자입니다.'), 403

            data = BoardUpdateSchema().load(json.loads(request.data))
            board = Board.objects(id=board_id, is_deleted=False).get()

            if board.is_duplicate(data['name']):
                return jsonify(message='이미 등록된 게시판입니다.'), 409

            board.update(**data)
            return '', 200

        except ValidationError as err:
            return err.messages, 422


    @route('/<board_id>', methods=['DELETE'])
    @login_required
    @check_board
    def delete(self, board_id):
        """
        게시판 삭제 API
        :param board_id: 게시판 objectId
        :return: message
        """
        if not g.master_role:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        board = Board.objects(id=board_id, is_deleted=False).get()
        board.update(is_deleted=True)

        return jsonify(message='삭제되었습니다.'), 200


    @route('/search', methods=['GET'])
    def search(self):
        """
        게시글 검색 API
        :return: 전체 게시판에서 검색된 게시글 10개
        """
        try:
            filtered_posts, page = PostFilterSchema().load(request.args)
            result = PaginatedPostsSchema().dump(filtered_posts.paginate(page=page, per_page=10))
            return result, 200

        except ValidationError as err:
            return err.messages, 422
        except:
            return jsonify(message='일치하는 결과가 없습니다.'), 400