import json

from app.models         import Board, Post, User
from app.serializers    import BoardSchema
from flask_classful     import FlaskView, route
from flask              import jsonify, request, g
from app.utils          import auth
from marshmallow        import ValidationError
from operator import itemgetter


class BoardView(FlaskView):
    # 게시판 카테고리 조회
    @route('/category', methods=['GET'])
    def get_category(self):
        board_data = Board.objects(is_deleted=False)

        board_category = [
            {"name": board.name}
            for board in board_data]

        return jsonify(data=board_category), 200


    # 게시판 생성
    @route('/boards', methods=['POST'])
    @auth
    def post(self):
        data = json.loads(request.data)

        # Validation
        try:
            BoardSchema().load(data)
        except ValidationError as err:
            return jsonify (err.messages), 422

        name = data['name']

        # 유저의 권한 확인
        if g.auth == False:
            return jsonify(message='권한이 없습니다.'), 403

        # 현재 존재하는 board와 이름 중복 확인
        if Board.objects(name=name, is_deleted=False):
            return jsonify(message='이미 등록된 게시판입니다.'), 400

        board = Board(name=name)
        board.save()

        return '', 200


    # 게시판 글 목록 조회
    @route('/<board_name>', methods=['GET'])
    def get(self, board_name):
        page = request.args.get('page', 1, int)

        # pagination
        limit = 10
        skip = (page - 1) * limit
        print(skip)
        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        post_list = Post.objects(board=board_id, is_deleted=False).order_by('-created_at').limit(limit).skip(skip)
        total_number_of_post = len(Post.objects(board=board_id, is_deleted=False))
        post_data=[
            {"total": total_number_of_post,
             "posts": [{"number": n,
                        "id": post.post_id,
                        "author":post.author.account,
                        "title": post.title,
                        "created_at": post.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
                        "likes": len(post.likes)}
                    for n, post in zip(range(total_number_of_post - skip, 0, -1), post_list)]}]

        return jsonify(post_data[0]), 200


    # 게시판 이름 수정
    @route('/<board_name>', methods=['PUT'])
    @auth
    def update(self, board_name):
        if not g.auth:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        data = json.loads(request.data)
        if Board.objects(name=board_name, is_deleted=False):
            Board.objects(name=board_name).update(name=data['board_name'])
            return '', 200

        return jsonify(message='없는 게시판입니다.'), 400

    # 게시판 삭제
    @route('/<board_name>', methods=['DELETE'])
    @auth
    def delete(self, board_name):
        if not g.auth:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        if Board.objects(name=board_name, is_deleted=False):
            Board.objects(name=board_name).update(is_deleted=True)
            return '', 200

        return jsonify(message='없는 게시판입니다.'), 400

    # 게시판 내 검색
    @route('/<board_name>/search', methods=['GET'])
    def search(self, board_name, filters=None):
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400

        board_id = Board.objects(name=board_name).get().id
        filters = request.args
        if filters is None:
            return jsonify(message='내용을 검색해주세요'), 400

        if 'title' in filters:
            posts = Post.objects(board=board_id, title__contains=filters['title'])

        if 'author' in filters:
            user_id = User.objects(account=filters['author']).get().id
            posts = Post.objects(board=board_id, author__contains=user_id)

        post = [post.to_json_list() for post in posts.all()]
        return jsonify({"total" : len(post),
                        "post" : post}), 200

    # 좋아요 순
    @route('/main/likes', methods=['GET'])
    def get_main_likes(self):
        posts = [post.to_json_list() for post in Post.objects]
        top_likes = sorted(posts, key=lambda post : post['likes'], reverse=True)[:9]

        return jsonify({"orderby_likes" : top_likes }), 200




    # 글 최신순 10개
    @route('/main/latest', methods=['GET'])
    def order_by_latest(self):
        posts = Post.objects(is_deleted=False).order_by('-created_at').limit(10)

        post = [post.to_json_list_with_board_name() for post in posts.all()]
        return jsonify(data=post),200


