import json

from flask_classful     import FlaskView, route
from flask              import jsonify, request, g
from marshmallow        import ValidationError

from app.utils          import login_required, check_board
from app.models         import Board, Post, User
from app.serializers    import BoardSchema


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
    @login_required
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
    @check_board
    def get(self, board_name):
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
                        "author":post.author.account,
                        "title": post.title,
                        "created_at": post.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
                        "likes": len(post.likes)}
                    for n, post in zip(range(total_number_of_post - skip, 0, -1), post_list)]}]

        return jsonify(post_data[0]), 200


    # 게시판 이름 수정
    @route('/<board_name>', methods=['PUT'])
    @login_required
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
    @login_required
    def delete(self, board_name):
        if not g.auth:
            return jsonify(message='권한이 없는 사용자입니다.'), 403

        if Board.objects(name=board_name, is_deleted=False):
            Board.objects(name=board_name).update(is_deleted=True)
            return '', 200

        return jsonify(message='없는 게시판입니다.'), 400


    # 게시판 내 검색
    # 매칭 쿼리 없을 때 오류 처리 필요(예은)
    @route('/<board_name>/search', methods=['GET'])
    @check_board
    def search(self, board_name, filters=None, posts=None):

        filters = request.args
        posts = Post.objects(board=g.board.id)

        # 속성__in argument는 순서를 맨앞으로 하면 잘 돌아가고, 맨 뒤에 넣으면 앞의 필터들이 리셋됨.
        if 'tag' in filters:
            tag = filters['tag'].split()
            posts = Post.objects(tag__in=tag)

        if 'title' in filters:
            posts = posts(title__contains=filters['title'])

        if 'author' in filters:
            user_id = User.objects(account=filters['author']).get().id
            posts = posts(author__exact=user_id)

        if filters is None or posts is None:
            return jsonify(message='내용을 검색해주세요'), 400

        post = [post.to_json_list() for post in posts.all()]
        return jsonify({"total" : len(post),
                        "post" : post}), 200


    # 좋아요 순
    @route('/main/likes', methods=['GET'])
    def get_main_likes(self):
        pipeline = [
            {"$project": {
                "number_of_likes": {"$size": "$likes"}}},
            {"$sort":
                 {"number_of_likes": -1}},
            {"$limit": 10}
        ]
        posts = Post.objects(is_deleted=False).aggregate(*pipeline)
        top_likes = [Post.objects(id=post['_id']).get().to_json_list() for post in posts]

        # posts = [post.to_json_list() for post in Post.objects]
        # top_likes = sorted(posts, key=lambda post : post['likes'], reverse=True)[:9]

        return jsonify({"orderby_likes" : top_likes}), 200


    # 글 최신순 10개
    @route('/main/latest', methods=['GET'])
    def order_by_latest(self):
        posts = Post.objects(is_deleted=False).order_by('-created_at').limit(10)

        post = [post.to_json_list() for post in posts.all()]
        return jsonify(data=post),200


    # 댓글 많은 순 10개
    @route('/main/comments', methods=['GET'])
    def order_by_latest(self):
        pipeline = [
            {"$lookup":
                 {"from": "comment",
                  "localField": "_id",
                  "foreignField": "post",
                  "as": "comments"}},
            {"$project": {
                "number_of_comment": {"$size": "$comments"}}},
            {"$sort": {"number_of_comment": -1}},
            {"$limit": 10}]

        posts = Post.objects(is_deleted=False).aggregate(*pipeline)
        post = [Post.objects(id=post['_id']).get().to_json_list() for post in posts]
        return jsonify(data=post), 200