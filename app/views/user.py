import json
import bcrypt

from app.models     import User
from flask_classful import FlaskView, route
from flask          import jsonify, request
from datetime       import datetime

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