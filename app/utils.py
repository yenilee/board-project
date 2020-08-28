import json
import jwt

from functools      import wraps
from flask          import request, g, jsonify
from bson.json_util import loads

from app.config     import SECRET, ALGORITHM
from app.models     import Board, Post, Comment


# 로그인 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not 'Authorization' in request.headers:
            return jsonify(message='로그인하지 않은 사용입니다.'), 403

        access_token = request.headers.get('Authorization')
        try:
            payload = jwt.decode(access_token, SECRET, ALGORITHM)

        except jwt.InvalidTokenError:
            return jsonify(message='유효하지 않은 토큰입니다'), 409

        g.user = loads(payload['user_id'])
        g.auth = payload['is_master']

        return f(*args, **kwargs)
    return decorated_function

# 게시판글 이름 존재 여부 체크
def check_board(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        board_name = kwargs['board_name']

        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        g.board = Board.objects(name=board_name, is_deleted=False).get()

        return f(*args, **kwargs)
    return decorated_view

# 게시글 번호 존재 여부 체크
def check_post(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        post_id = kwargs['post_id']

        if not Post.objects(board=g.board.id,post_id=post_id, is_deleted=False):
            return jsonify(message="없는 게시물입니다."), 200
        g.post = Post.objects(board=g.board.id, post_id=post_id, is_deleted=False).get()

        return f(*args, **kwargs)
    return decorated_view

# 댓글 objectId 존재 여부 체크
def check_comment(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        comment_id = kwargs['comment_id']

        if len(comment_id) is not 24:
            return jsonify(message='유효한 댓글ID가 아닙니다.'), 400

        if not Comment.objects(post=g.post.id, id=comment_id, is_deleted=False):
            return jsonify(message='없는 댓글입니다.'), 400

        g.comment = Comment.objects(post=g.post.id, is_deleted=False, id=comment_id).get()

        return f(*args, **kwargs)
    return decorated_view