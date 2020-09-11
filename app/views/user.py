import json
import bcrypt
import jwt

from flask_classful import FlaskView, route
from flask import jsonify, request, g, current_app
from bson.json_util import dumps

from app.models import User, Post, Comment
from app.utils import login_required, user_validator, pagination, user_create_validator
from app.serializers.user import UserCreateSchema
from app.serializers.post import PostListSchema, PaginatedPostsSchema
from app.serializers.comment import CommentListSchema


class UserView(FlaskView):
    @route('/signup', methods=['POST'])
    @user_create_validator
    def signup(self):
        """"
        회원가입 API
        작성자: dana
        :return: message
        """
        user = UserCreateSchema().load(json.loads(request.data))

        if user is False:
            return {'message': '이미 등록된 ID입니다.'}, 409

        user.save()
        return '', 200


    @route('/signin', methods=['POST'])
    @user_validator
    def signin(self):
        """
        로그인 API
        작성자: avery
        :return: 로그인 인증 토큰
        """
        data = json.loads(request.data)

        if not User.objects(account=data['account']):
            return jsonify(message='존재하지 않는 ID입니다.'), 401

        user = User.objects(account=data['account']).get()

        if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
            token = jwt.encode({"user_id" : dumps(user.id),
                                "is_master" : user.master_role}, current_app.config['SECRET'], current_app.config['ALGORITHM'])
            return jsonify(token.decode('utf-8')), 200

        return jsonify(message='잘못된 비밀번호 입니다.'), 401


    @route('/posts', methods=['GET'])
    @login_required
    def my_post(self):
        """
        마이페이지: 사용자 작성 게시물 조회 API
        작성자: avery
        :return: 최신 게시물 10개
        """
        posts = Post.objects(author=g.user_id, is_deleted=False).order_by('-created_at').limit(20)
        my_page = PostListSchema(many=True).dump(posts)
        return jsonify(my_posts=my_page), 200


    @route('/comments', methods=['GET'])
    @login_required
    def my_comment(self):
        """
        마이페이지: 사용자 작성 댓글 조회 API
        작성자: avery
        :return: 최신 댓글 10개
        """
        comments = Comment.objects(author=g.user_id, is_deleted=False, is_reply=False)
        my_comments = CommentListSchema(many=True).dump(comments)
        return jsonify(my_comments=my_comments), 200


    @route('/liked-posts', methods=['GET'])
    @login_required
    def my_liked_post(self, page=1):
        """
        마이페이지: 사용자가 좋아요 한 글 조회 API
        작성자: dana
        :return: 좋아요 한 글 10
        """
        if request.args:
            page = int(request.args.get('page'))

        posts = Post.objects(likes__exact=str(g.user_id), is_deleted=False).order_by('created_at').paginate(page=page, per_page=10)
        liked_posts = PaginatedPostsSchema().dump(posts)

        return liked_posts, 200