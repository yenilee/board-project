import json
import jwt

from functools import wraps
from flask import request, g, jsonify, current_app
from bson.json_util import loads
from marshmallow import ValidationError

from app.models import Board, Post, Comment
from app.serializers.user import UserSchema, UserCreateSchema
from app.serializers.board import BoardCreateSchema
from app.serializers.comment import CommentUpdateSchema, CommentCreateSchema
from app.serializers.post import PostUpdateSchema, PostCreateSchema


# 로그인 인증 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not 'Authorization' in request.headers:
            return jsonify(message='로그인하지 않은 사용자입니다.'), 401

        try:
            access_token = request.headers.get('Authorization')
            payload = jwt.decode(access_token, current_app.config['SECRET'], current_app.config['ALGORITHM'])

        except jwt.InvalidTokenError:
            return jsonify(message='유효하지 않은 토큰입니다'), 401

        g.user_id = loads(payload['user_id'])
        g.master_role = payload['is_master']

        return f(*args, **kwargs)
    return decorated_function

# 게시판글 이름 존재 여부 체크
def check_board(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        board_id = kwargs['board_id']

        if not Board.objects(id=board_id, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 404

        return f(*args, **kwargs)
    return decorated_view

# 게시글 번호 존재 여부 체크
def check_post(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        board_id = kwargs['board_id']
        post_id = kwargs['post_id']

        if not Post.objects(board=board_id, id=post_id, is_deleted=False):
            return jsonify(message="없는 게시물입니다."), 404

        return f(*args, **kwargs)
    return decorated_view

# 댓글 objectId 존재 여부 체크
def check_comment(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        post_id = kwargs['post_id']
        comment_id = kwargs['comment_id']

        if len(comment_id) is not 24 or type(comment_id) is not str:
            return jsonify(message='유효한 댓글ID가 아닙니다.'), 400

        if not Comment.objects(post=post_id, id=comment_id, is_deleted=False):
            return jsonify(message='없는 댓글입니다.'), 404

        return f(*args, **kwargs)
    return decorated_view

# 게시글 validation check
def post_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            PostCreateSchema().load(json.loads(request.data))

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

# 회원가입 validation check
def user_create_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            UserCreateSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view

# board create validation check
def board_create_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            BoardCreateSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view

# comment update validation check
def comment_update_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            CommentUpdateSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view

# comment create validation check
def comment_create_validator(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        try:
            CommentCreateSchema().load(json.loads(request.data))

        except ValidationError as err:
            return jsonify(err.messages), 422

        return f(*args, **kwargs)
    return decorated_view
