import json

from app.models         import Board, Post, User
from flask_classful     import FlaskView, route
from flask              import jsonify, request, g
from app.utils          import auth


class BoardView(FlaskView):
    # 게시판 카테고리
    @route('/category', methods=['GET'])
    def get_board_category(self):
        board_data = Board.objects(is_deleted = False)

        board_category = [
            {"name": board.name}
        for board in board_data]

        return jsonify(data=board_category), 200


    # 게시판 생성
    @route('', methods=['POST'])
    @auth
    def post(self):
        name = json.loads(request.data)['name']

        # 유저의 권한 확인
        if User.objects(id=g.user).get().master_role == False:
            return jsonify(message='권한이 없습니다.'),403

        # 현재 존재하는 board와 이름 중복 확인
        if Board.objects(name=name, is_deleted=False):
            return jsonify(message='이미 등록된 게시판입니다.'), 400

        board = Board(name=name)
        board.save()

        return '', 200


    # 게시판 목록 조회
    @route('/', methods=['GET'])
    def list_board(self):
        category = request.args['category']
        page = request.args.get('page',1,int)

        # pagination
        limit = 10
        skip = (page-1)*limit

        if Board.objects(name=category, is_deleted=False):
            post_list = Board.objects(name=category, is_deleted=False).get().post
            post_data = [
                {"total": len(post_list),
                 "posts": [{"post_id": post.post_id,
                            "title": post.title,
                            "content": post.content,
                            "created_at": post.created_at,
                            "likes": len(post.likes)} for post in post_list[skip:skip + limit]]
                 }]
            return jsonify(data=post_data), 200
        return jsonify(message='없는 게시판입니다.'), 400


    # 게시글 작성 API
    @route('/<board_name>/post', methods=['POST'])
    @auth
    def create_post(self, board_name):
        data = json.loads(request.data)

        board = Board.objects(name=board_name).get()
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

        try:
            post = Board.objects(name=board_name, is_deleted=False).get().post[post_id-1]
            return jsonify(post.to_json()), 200
        except:
            return jsonify(message='없는 게시물입니다.'), 400
