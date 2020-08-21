import json
import bcrypt
import jwt

from app.models     import User
from flask_classful import FlaskView, route
from flask          import jsonify, request
from app.config     import SECRET, ALGORITHM
from app.utils      import JSONEncoder


class UserView(FlaskView):
    # 회원가입
    @route('/signup', methods=['POST'])
    def signup(self):
        data = json.loads(request.data)

        account = data['account']
        password = data['password']

        # account 중복 확인
        if User.objects(account=account):
            return jsonify(message='이미 등록된 account입니다.'), 409

        # password_hash
        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # user 정보 저장
        user = User(account=account,
                password=password
                )
        user.save()
        return '', 200


    @route('/signin', methods=['POST'])
    def post(self, user=None):
        data = json.loads(request.data)
        user = User.objects(account=data['account'])

        if user:
            for user in user:
                user_password = user.password
                user_id = json.dumps(user.id, cls=JSONEncoder)

            if bcrypt.checkpw(data['password'].encode('utf-8'), user_password.encode('utf-8')):
                token = jwt.encode({'id': user_id}, SECRET, ALGORITHM)
                return jsonify(token.decode('utf-8')), 200

            return jsonify(message='잘못된 비밀번호 입니다.'), 400
        return jsonify(message='존재하지 않는 ID입니다.'), 400