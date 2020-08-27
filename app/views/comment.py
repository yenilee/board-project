import json

from app.models import Board, Post, Comment
from flask_classful import FlaskView, route
from flask import jsonify, request, g
from app.utils import auth
from bson.json_util import loads, dumps


class CommentView(FlaskView):

    # 댓글 생성
    @route('', methods=['POST'])
    @auth
    def post(self, board_name, post_id):
        data = json.loads(request.data)

        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        # 게시글 존재 여부 확인
        if not Post.objects(board=board_id, post_id=post_id, is_deleted=False):
            return jsonify(message='잘못된 주소입니다.'), 400
        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False).get().id

        comment = Comment(
            post=post,
            author=g.user,
            content=data['content'],
        )
        comment.save()
        return jsonify(message='댓글이 등록되었습니다.'), 200

    # 댓글 수정
    @route('<comment_id>', methods=['PUT'])
    @auth
    def update(self, board_name, post_id, comment_id):
        data = json.loads(request.data)

        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        # 게시글 존재 여부 확인
        if not Post.objects(board=board_id, post_id=post_id, is_deleted=False):
            return jsonify(message='잘못된 주소입니다.'), 400
        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False).get().id

        comment = Comment.objects(id=comment_id).get()
        if comment.author.id == g.user and comment.is_deleted is False:
            comment['content'] = data['content']
            comment.save()
            return jsonify(message='댓글이 수정되었습니다.'), 200

        return jsonify(message='수정 권한이 없습니다.'), 401


    # 댓글 삭제
    @route('<comment_id>', methods=['DELETE'])
    @auth
    def delete(self, board_name, post_id, comment_id):

        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        # 게시글 존재 여부 확인
        if not Post.objects(board=board_id, post_id=post_id, is_deleted=False):
            return jsonify(message='잘못된 주소입니다.'), 400
        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False).get()

        # 삭제 가능 user 확인
        comment = Comment.objects(id=comment_id).get()
        if comment.author.id == g.user and comment.is_deleted is False:
            comment.is_deleted = True
            comment.save()
            return jsonify(message='댓글이 삭제되었습니다.'), 200

        return jsonify(message='수정 권한이 없습니다.'), 401


    # 댓글 좋아요 및 취소 API
    @route('/<comment_id>/likes', methods=['POST'])
    @auth
    def like_post(self, board_name, post_id, comment_id):
        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        # 게시글 존재 여부 확인
        if not Post.objects(board=board_id, post_id=post_id, is_deleted=False):
            return jsonify(message='잘못된 주소입니다.'), 400
        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False).get()

        # 댓글 존재 여부 확인
        if not Comment.objects(post=post, id=comment_id, is_deleted=False):
            return jsonify(message='잘못된 주소입니다.'), 400
        comment = Comment.objects(post=post, is_deleted=False, id=comment_id).get()

        likes_user = {}
        for user_index_number in range(0,len(comment.likes)):
            likes_user[comment.likes[user_index_number].id] = user_index_number

        # 좋아요 누른 경우 --> 취소
        if g.user in likes_user.keys():
            user_index = likes_user[g.user]
            del comment.likes[user_index]
            comment.save()
            return jsonify(message="'좋아요'가 취소되었습니다."), 200

        # 좋아요 누르지 않은 경우 --> 좋아요
        comment.likes.append(g.user)
        comment.save()
        return jsonify(message="'좋아요'가 반영되었습니다."), 200


    # 대댓글 생성 API
    @route('/<comment_id>/reply', methods=['POST'])
    @auth
    def post_reply(self, board_name, post_id, comment_id):
        data = json.loads(request.data)

        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        # 게시글 존재 여부 확인
        if not Post.objects(board=board_id, post_id=post_id, is_deleted=False):
            return jsonify(message='잘못된 주소입니다.'), 400
        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False).get()

        # 댓글 존재 여부 확인
        if not Comment.objects(post=post, id=comment_id, is_deleted=False):
            return jsonify(message='잘못된 주소입니다.'), 400
        comment = Comment.objects(post=post, is_deleted=False, id=comment_id).get()

        reply = Comment(
            post=post,
            author=g.user,
            replied_comment=comment,
            content=data['content'],
        )
        reply.save()


        return jsonify(message='댓글이 등록되었습니다.'), 200