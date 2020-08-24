import json
import jwt

from bson           import ObjectId
from functools      import wraps
from flask          import request, g, jsonify
from app.config     import SECRET, ALGORITHM
from bson.json_util import loads

# class JSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)

# 로그인 데코레이터
def auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not 'Authorization' in request.headers:
            return jsonify(message='로그인 권한이 없습니다.'), 403

        access_token = request.headers.get('Authorization')
        try:
            payload = jwt.decode(access_token, SECRET, ALGORITHM)

        except jwt.InvalidTokenError:
            return jsonify(message='유효하지 않은 토큰입니다'), 409

        g.user = loads(payload['user_id'])
        g.auth = payload['is_master']

        return f(*args, **kwargs)
    return decorated_function