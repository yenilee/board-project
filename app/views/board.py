import json

from app.models         import Board, Post, User
from app.serializers    import BoardSchema
from flask_classful     import FlaskView, route
from flask              import jsonify, request, g
from app.utils          import auth
from marshmallow        import ValidationError


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
    @route('', methods=['POST'])
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


    # 게시판 글목록 조회
    @route('/<board_name>', methods=['GET'])
    def get(self, board_name):
        page = request.args.get('page', 1, int)

        # pagination
        limit = 10
        skip = (page - 1) * limit

        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        post_list = Post.objects(board=board_id, is_deleted=False).order_by('-created_at')
        post_data=[
            {"total": len(post_list),
             "posts": [{"number": n,
                        "post_id": post.post_id,
                        "title": post.title,
                        "created_at": post.created_at,
                        "likes": len(post.likes)}
                    for n, post in zip(range(len(post_list) - skip, 0, -1), post_list[skip:skip + limit])]}]

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
            return '',200

        return jsonify(message='없는 게시판입니다.'), 400

    # 게시판 삭제
    @route('/<board_name>', methods=['DELETE'])
    @auth
    def delete(self, board_name):
        if not g.auth:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        if Board.objects(name=board_name, is_deleted=False):
            Board.objects(name=board_name).update(is_deleted=True)
            return '',200

        return jsonify(message='없는 게시판입니다.'), 400

    # 게시판 내 검색
    @route('/<board_name>/search', methods=['GET'])
    def search(self, board_name, filters=None):
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400

        board_id = Board.objects(name=board_name).get().id
        filters = request.args

        if 'title' in filters:
            posts = Post.objects(board=board_id, title__contains=filters['title'])

        if 'author' in filters:
            user_id = User.objects(account=filters['author']).get().id
            posts = Post.objects(board=board_id, author__contains=user_id)

        post = [post.to_json_list() for post in posts.all()]
        return jsonify({"total" : len(post),
                        "post" : post}), 200








