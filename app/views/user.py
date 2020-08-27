import json
import bcrypt
import jwt

from app.models         import User, Post, Comment
from app.serializers    import UserSchema
from flask_classful     import FlaskView, route
from flask              import jsonify, request, g
from app.config         import SECRET, ALGORITHM
from marshmallow        import ValidationError
from bson.json_util     import dumps
from app.utils          import auth


class UserView(FlaskView):
    # 회원가입
    @route('/signup', methods=['POST'])
    def signup(self):
        data = json.loads(request.data)

        # Validation
        try:
            UserSchema().load(data)
        except ValidationError as err:
            return jsonify (err.messages), 422

        account = data['account']
        password = data['password']

        # account 중복 확인
        if User.objects(account=account):
            return jsonify(message='이미 등록된 ID입니다.'), 409

        # password_hash
        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # user 정보 저장
        user = User(account=account,
                password=password
                )
        user.save()
        return '', 200


    # 로그인
    @route('/signin', methods=['POST'])
    def signin(self, user=None):
        data = json.loads(request.data)
        user = User.objects(account=data['account'])

        if not user:
            return jsonify(message='존재하지 않는 ID입니다.'), 401

        for user in user:
            if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                token = jwt.encode({"user_id" : dumps(user.id),
                                    "is_master" : user.master_role}, SECRET, ALGORITHM)
                return jsonify(token.decode('utf-8')), 200

        return jsonify(message='잘못된 비밀번호 입니다.'), 401


    # 내 게시물
    @route('/mypage', methods=['GET'])
    @auth
    def my_post(self):
        if g.user:
            my_post = [my_post.to_json_list() for my_post in Post.objects(author=g.user).all()]
            return {"my_post":my_post}, 200


    # 내 댓글
    @route('/mypage/comment', methods=['GET'])
    @auth
    def my_comment(self):
        if not g.user:
            return jsonify(message='로그인하지 않은 사용자입니다.'), 400

        my_comment = [comment.to_json() for comment in Comment.objects(author=g.user)]

        return {"my_comment" : my_comment }, 200


    # 좋아요 한 글
    @route('/mypage/likes', methods=['GET'])
    @auth
    def my_liked_post(selfs):

        posts = Post.objects(likes__contains = g.user, is_deleted = False)
        post = [post.to_json_list_with_board_name() for post in posts.all()]

        return jsonify(data=post), 200