import json

from flask_classful import FlaskView, route
from flask import jsonify, request, g

from app.utils import login_required, check_board, board_validator, pagination
from app.models import Board, Post, User


class BoardView(FlaskView):
    @route('', methods=['GET'])
    def get_category(self):
        """
        게시판 카테고리 조회 API
        작성자: dana
        :return: 게시판 카테고리
        """
        board_data = Board.objects(is_deleted=False)

        board_category = [
            {"name": board.name}
            for board in board_data]

        return jsonify(data=board_category), 200


    @route('', methods=['POST'])
    @login_required
    @board_validator
    def post(self):
        """
        게시판 생성 API
        작성자: dana
        :return: message
        """
        # 유저의 권한 확인
        if not g.auth:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        data = json.loads(request.data)
        board_name = data['board_name']

        # 현재 존재하는 board와 이름 중복 확인
        if Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='이미 등록된 게시판입니다.'), 409

        board = Board(name=board_name)
        board.save()

        return jsonify(message='등록되었습니다.'), 200


    @route('/<board_id>', methods=['GET'])
    @check_board
    def get(self, board_id):
        """
        게시판 글 조회 API
        작성자: dana
        :param board_id: 게시판 objectId
        :return: 게시판 글 목록 (제목, 내용, 작성자 등)
        """
        page = request.args.get('page', 1, int)

        # pagination
        limit = 10
        skip = (page - 1) * limit

        post_list = Post.objects(board=g.board.id, is_deleted=False).order_by('-created_at').limit(limit).skip(skip)
        total_number_of_post = Post.objects(board=g.board.id, is_deleted=False).count()
        post_data=[
            {"total": total_number_of_post,
             "posts": [{"number": n,
                        "id": post.post_id,
                        "author": post.author.account,
                        "title": post.title,
                        "created_at": post.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
                        "likes": len(post.likes)}
                    for n, post in zip(range(total_number_of_post - skip, 0, -1), post_list)]}]

        return jsonify(post_data[0]), 200


    @route('/<board_id>', methods=['PUT'])
    @login_required
    @check_board
    @board_validator
    def update(self, board_id):
        """
        게시판 이름 수정 API
        작성자: avery
        :param board_id: 게시판 objectId
        :return: message
        """
        # 유저의 권한 확인
        if not g.auth:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        data = json.loads(request.data)

        # 변경할 게시판 이름 중복 여부 체크
        if Board.objects(name=data['board_name'], is_deleted=False):
            return jsonify(message='이미 등록된 게시판입니다.'), 409

        g.board.update(name=data['board_name'])
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
        if not g.auth:
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
        posts = Post.objects(board=g.board.id)

        # 속성__in argument는 순서를 맨앞으로 하면 잘 돌아가고, 맨 뒤에 넣으면 앞의 필터들이 리셋됨.
        if 'tag' in filters:
            tag = filters['tag'].split()
            posts = Post.objects(board=g.board.id, tag__in=tag)

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
        post = [post.to_json_list() for post in posts.all()]
        return jsonify(data=post),200


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