import json
import bcrypt
import jwt

from flask_classful import FlaskView, route
from flask import jsonify, request, g, current_app
from bson.json_util import dumps

from app.models import User, Post, Comment
from app.config import Config
from app.utils import login_required, user_validator, pagination


class UserView(FlaskView):
    @route('/signup', methods=['POST'])
    @user_validator
    def signup(self):
        """"
        회원가입 API
        작성자: dana
        :return: message
        """
        data = json.loads(request.data)

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
        return jsonify(message='등록되었습니다.'), 200


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


    @route('/mypage', methods=['GET'])
    @login_required
    def my_post(self):
        """
        마이페이지: 사용자 작성 게시물 조회 API
        작성자: avery
        :return: 최신 게시물 10개
        """
        posts = Post.objects(author=g.user, is_deleted=False)
        number_of_posts = len(posts)

        my_post = [my_post.to_json_list() for my_post in
                   pagination(posts.all().order_by('-created_at'))]
        return jsonify({"my_post": my_post,
                        "number_of_posts": number_of_posts}), 200


    @route('/mypage/comment', methods=['GET'])
    @login_required
    def my_comment(self):
        """
        마이페이지: 사용자 작성 댓글 조회 API
        작성자: avery
        :return: 최신 댓글 10개
        """
        comments = Comment.objects(author=g.user, is_deleted=False)
        number_of_comments = len(comments)

        my_comment = [comment.to_json() for comment in
                      pagination(comments.all().order_by('-created_at'))]
        return jsonify({"my_comment":my_comment,
                        "number_of_comments":number_of_comments}), 200


    @route('/mypage/likes', methods=['GET'])
    @login_required
    def my_liked_post(self):
        """
        마이페이지: 사용자가 좋아요 한 글 조회 API
        작성자: dana
        :return: 좋아요 한 글 10
        """
        posts = Post.objects(likes__exact=g.user, is_deleted=False)
        number_of_posts = len(posts)

        my_post = [post.to_json_list() for post in
                pagination(posts.all().order_by('created_at'))]

        return jsonify({"my_post": my_post,
                        "number_of_posts": number_of_posts}), 200