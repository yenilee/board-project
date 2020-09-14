import json
import jwt

from flask_classful import FlaskView, route
from flask import jsonify, request, g, current_app
from bson.json_util import dumps

from app.models import Post, Comment
from app.utils import login_required, user_validator, user_create_validator
from app.serializers.user import UserCreateSchema, UserSchema
from app.serializers.post import PaginatedPostsSchema, PaginatedPostsInBoardSchema
from app.serializers.comment import PaginatedCommentsSchema


class UserView(FlaskView):
    @route('/signup', methods=['POST'])
    @user_create_validator
    def signup(self):
        """"
        회원가입 API
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
        :return: 로그인 인증 토큰
        """
        login_request = json.loads(request.data)
        user = UserSchema().load(login_request)

        if not user:
            return {'message': '존재하지 않는 사용자입니다.'}, 401

        if not user.check_password(login_request['password']):
            return {'message': '잘못된 비밀번호 입니다.'}, 401

        token = jwt.encode({"user_id": dumps(user.id), "is_master": user.master_role},
                           current_app.config['SECRET'], current_app.config['ALGORITHM'])

        return jsonify(token.decode('utf-8')), 200


    @route('/posts', methods=['GET'])
    @login_required
    def my_posts(self, page=1):
        """
        마이페이지: 사용자 작성 게시물 조회 API
        :return: 최신 게시물 10개
        """
        if request.args:
            page = int(request.args.get('page'))

        recent_10_posts_by_user = Post.objects(author=g.user_id, is_deleted=False).order_by('-created_at').paginate(page=page, per_page=10)
        my_posts = PaginatedPostsInBoardSchema().dump(recent_10_posts_by_user)
        return jsonify(my_posts), 200


    @route('/comments', methods=['GET'])
    @login_required
    def my_comments(self, page=1):
        """
        마이페이지: 사용자 작성 댓글 조회 API
        :return: 최신 댓글 10개
        """
        if request.args:
            page = int(request.args.get('page'))

        recent_10_comments_by_user = Comment.objects(author=g.user_id, is_deleted=False, is_reply=False).order_by('-created_at').paginate(page=page, per_page=10)
        my_comments = PaginatedCommentsSchema().dump(recent_10_comments_by_user)
        return jsonify(my_comments), 200


    @route('/liked-posts', methods=['GET'])
    @login_required
    def my_liked_post(self, page=1):
        """
        마이페이지: 사용자가 좋아요 한 글 조회 API
        :return: 좋아요 한 글 10
        """
        if request.args:
            page = int(request.args.get('page'))

        recent_10_liked_posts = Post.objects(likes__exact=str(g.user_id), is_deleted=False).order_by('-created_at').paginate(page=page, per_page=10)
        my_liked_posts = PaginatedPostsSchema().dump(recent_10_liked_posts)

        return my_liked_posts, 200
