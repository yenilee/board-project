import json
import jwt

from functools import wraps
from flask import request, g, jsonify, current_app
from bson.json_util import loads
from marshmallow import ValidationError

from app.models import Board, Post, Comment
from app.serializers.user import UserSchema
from app.serializers.board import BoardSchema
from app.serializers.comment import CommentSchema
from app.serializers.post import PostSchema, PostUpdateSchema


# 로그인 인증 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not 'Authorization' in request.headers:
            return jsonify(message='로그인하지 않은 사용입니다.'), 401

        access_token = request.headers.get('Authorization')
        try:
            payload = jwt.decode(access_token, current_app.config['SECRET'], current_app.config['ALGORITHM'])

        except jwt.InvalidTokenError:
            return jsonify(message='유효하지 않은 토큰입니다'), 401

        g.user = loads(payload['user_id'])
        g.auth = payload['is_master']

        return f(*args, **kwargs)
    return decorated_function

# 게시판글 이름 존재 여부 체크
def check_board(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        board_id = kwargs['board_id']

        if not Board.objects(id=board_id, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 404
        g.board = Board.objects(id=board_id, is_deleted=False).get()

        return f(*args, **kwargs)
    return decorated_view

# 게시글 번호 존재 여부 체크
def check_post(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        post_id = kwargs['post_id']

        if not Post.objects(board=g.board.id, id=post_id, is_deleted=False):
            return jsonify(message="없는 게시물입니다."), 404
        g.post = Post.objects(board=g.board.id, id=post_id, is_deleted=False).get()

        return f(*args, **kwargs)
    return decorated_view

# 댓글 objectId 존재 여부 체크
def check_comment(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        comment_id = kwargs['comment_id']
        if len(comment_id) is not 24 or type(comment_id) is not str:
            return jsonify(message='유효한 댓글ID가 아닙니다.'), 400

        if not Comment.objects(post=g.post.id, id=comment_id, is_deleted=False):
            return jsonify(message='없는 댓글입니다.'), 404

        g.comment = Comment.objects(post=g.post.id, is_deleted=False, id=comment_id).get()

        return f(*args, **kwargs)
    return decorated_view

# 게시글 validation check
def post_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            PostSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view

# 게시글 validation check
def post_update_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            PostUpdateSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view


# 유저 validation check
def user_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            UserSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view

# board validation check
def board_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            BoardSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view

# comment validation check
def comment_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            CommentSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view

# 객체를 받아 페이지네이션 기능을 추가해주는 함수
def pagination(obj, order_by='created_at', page=1, limit=10):
    listed_object = obj.order_by(order_by).limit(limit).skip((page - 1) * limit)
    return listed_object