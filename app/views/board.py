import json

from flask_classful import FlaskView, route
from flask import jsonify, request, g
from marshmallow import ValidationError

from app.utils import login_required, check_board, board_create_validator
from app.models import Board, Post, User
from app.serializers.board import BoardCategorySchema, BoardCreateSchema, BoardUpdateSchema
from app.serializers.post import PostListSchema, PaginatedPostsInBoardSchema, HighRankingPostListSchema, PaginatedPostsSchema, PostFilterSchema


class BoardView(FlaskView):
    @route('/categories', methods=['GET'])
    def get_category(self):
        """
        게시판 카테고리 조회 API
        작성자: dana
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
        작성자: dana
        :return: message
        """
        # Permission Check
        if g.master_role is False:
            return {'message': '권한이 없는 사용자입니다.'}, 403

        board = BoardCreateSchema().load(json.loads(request.data))

        if board is False:
            return {'message': '이미 등록된 게시판입니다.'}, 400

        board.save()
        return '', 200


    @route('/<board_id>', methods=['GET'])
    @check_board
    def get(self, board_id, page=1):
        """
        게시판 글 조회 API
        작성자: dana
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
        작성자: avery
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
        작성자: avery
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
        작성자: avery
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


    @route('/ranking/likes', methods=['GET'])
    def get_main_likes(self):
        """
        메인페이지: 좋아요 많은 글 조회 API
        작성자: avery
        :return: 좋아요 기준 게시글 10개
        """
        pipeline = [
            {"$project": {
                "board": "$board",
                "title": "$title",
                "author": "$author",
                "total_likes_count" : {"$size" :"$likes"}}},
            {"$sort": {"total_likes_count": -1}},
            {"$limit": 10}
        ]
        posts = Post.objects(is_deleted=False).aggregate(pipeline)
        post_list = HighRankingPostListSchema(many=True).dump(posts)

        return jsonify({"most_liked_posts": post_list}), 200


    @route('/ranking/latest', methods=['GET'])
    def order_by_latest(self):
        """
        메인페이지: 최신 글 조회 API
        작성자: dana
        :return: 최신 게시글 10개
        """
        posts = Post.objects(is_deleted=False).order_by('-created_at').limit(10)
        latest_post_list = PostListSchema(many=True).dump(posts)
        return {'latest_post_list': latest_post_list}, 200


    @route('/ranking/comments', methods=['GET'])
    def order_by_comments(self):
        """
        메인페이지: 댓글 많은 글 조회 API
        작성자: dana
        :return: 댓글 기준 게시글 10개
        """
        pipeline = [
            {"$lookup": {"from": "comment",
                         "let": {"id": "$_id"},
                         "pipeline": [
                             {"$match":
                                  {"$expr": {"$eq": ["$post", "$$id"]},
                                   "is_deleted": False}}],
                         "as": "comments"}},
            {"$project": {
                "board": "$board",
                "title": "$title",
                "author": "$author",
                "total_comments_count": {"$size": "$comments"},
                "total_likes_count": {"$size": "$likes"}}},
            {"$sort": {"total_comments_count": -1}},
            {"$limit": 10}
        ]

        posts = Post.objects(is_deleted=False).aggregate(pipeline)
        post_list = HighRankingPostListSchema(many=True).dump(posts)
        return {'post_list': post_list}, 200