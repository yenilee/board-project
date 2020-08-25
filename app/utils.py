import json
import jwt

from functools      import wraps
from flask          import request, g, jsonify
from app.config     import SECRET, ALGORITHM
from bson.json_util import loads
from app.models     import Board


# 로그인 데코레이터
def auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not 'Authorization' in request.headers:
            return jsonify(message='로그인하지 않은 유저입니다.'), 403

        access_token = request.headers.get('Authorization')
        try:
            payload = jwt.decode(access_token, SECRET, ALGORITHM)

        except jwt.InvalidTokenError:
            return jsonify(message='유효하지 않은 토큰입니다'), 409

        g.user = loads(payload['user_id'])
        g.auth = payload['is_master']

        return f(*args, **kwargs)
    return decorated_function

def check_board(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(args)
        # if not Board.objects(name=board_name, is_deleted=False):
        #     return jsonify(message='없는 게시판입니다.'), 400
        # board_id = Board.objects(name=board_name, is_deleted=False).get().id

        return f(*args, **kwargs)
    return decorated()