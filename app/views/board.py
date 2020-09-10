import json

from flask_classful import FlaskView, route
from flask import jsonify, request, g

from app.utils import login_required, check_board, board_create_validator, pagination
from app.models import Board, Post, User
from app.serializers.board import BoardCategorySchema, BoardCreateSchema
from app.serializers.post import PostListSchema, PaginatedPostsInBoardSchema


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
    # @board_validator
    def update(self, board_id):
        """
        게시판 이름 수정 API
        작성자: avery
        :param board_id: 게시판 objectId
        :return: message
        """
        # Permission Check
        if not g.master_role:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        data = json.loads(request.data)

        # 변경할 게시판 이름 중복 여부 체크
        if Board.objects(name=data['board_name'], is_deleted=False):
            return jsonify(message='이미 등록된 게시판입니다.'), 409

        Board.objects(id=board_id).update(name=data['board_name'])
        return jsonify(message='수정되었습니다.'), 200


    @route('/<board_id>', methods=['DELETE'])
    @login_required
    def delete(self, board_id):
        """
        게시판 삭제 API
        작성자: avery
        :param board_id: 게시판 objectId
        :return: message
        """
        if not g.master_role:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        if Board.objects(id=board_id, is_deleted=False):
            Board.objects(id=board_id).update(is_deleted=True)
            return jsonify(message='삭제되었습니다.'), 200

        return jsonify(message='없는 게시판입니다.'), 404


    @route('/<board_id>/search', methods=['GET'])
    @check_board
    def search(self, board_id, filters=None, posts=None):
        """
        게시글 검색 API
        작성자: avery
        :param board_id: 게시판 objectId
        :param filters: 필터(태그, 글제목, 작성자)
        :param posts: 게시글 객체
        :return: 검색된 게시글 10개
        """
        filters = request.args
        posts = Post.objects(board=board_id)

        # 속성__in argument는 순서를 맨앞으로 하면 잘 돌아가고, 맨 뒤에 넣으면 앞의 필터들이 리셋됨.
        if 'tags' in filters:
            tags = filters['tags'].split()
            posts = Post.objects(board=board_id, tags__in=tags)

        if 'title' in filters:
            posts = posts(title__contains=filters['title'])

        if 'author' in filters:
            user_id = User.objects(account=filters['author']).get().id
            posts = posts(author__exact=user_id)

        if filters is None or posts is None:
            return jsonify(message='내용을 검색해주세요'), 400

        number_of_posts = len(posts)

        # 필터링한 객체들을 받아 json형태로 만들고, 페이지네이션

        post = [post.to_json_list() for post in
                pagination(posts.all().order_by('-post_id'))]

        return jsonify({"total": number_of_posts, "post": post}), 200


    @route('/ranking/likes', methods=['GET'])
    def get_main_likes(self):
        """
        메인페이지: 좋아요 많은 글 조회 API
        작성자: avery
        :return: 좋아요 기준 게시글 10개
        """
        pipeline = [
            {"$project": {
                "number_of_likes": {"$size": "$likes"}}},
            {"$sort":
                 {"number_of_likes": -1}},
            {"$limit": 10}
        ]
        posts = Post.objects(is_deleted=False).aggregate(pipeline)
        top_likes = [Post.objects(id=post['_id']).get().to_json_list() for post in posts]

        # posts = [post.to_json_list() for post in Post.objects]
        # top_likes = sorted(posts, key=lambda post : post['likes'], reverse=True)[:9]

        return jsonify({"orderby_likes": top_likes}), 200


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
                "number_of_comment": {"$size": "$comments"}}},
            {"$sort": {"number_of_comment": -1}},
            {"$limit": 10}
        ]

        posts = Post.objects(is_deleted=False).aggregate(pipeline)
        post = [Post.objects(id=post['_id']).get().to_json_list() for post in posts]
        return jsonify(data=post), 200