import json

from app.models     import User
from flask_classful import FlaskView, route
from flask          import jsonify, request
from datetime       import datetime

class UserView(FlaskView):

    @route('/test_get', methods=['GET'])
    def get(self):
        user = User.objects.first()
        return jsonify(user.to_json()), 200

    @route('/test_post', methods=['POST'])
    def post(self):
        record = json.loads(request.data)
        user = User(account=record['account'],
                    password=record['password'],
                    created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        user.save()
        return '', 200

