import json

from app.models import Board, Post, Comment
from flask_classful import FlaskView, route
from flask import jsonify, request, g
from app.utils import auth


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

        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False)

        # 게시글 존재 여부 확인
        if not post:
            return jsonify(message='잘못된 주소입니다.'), 400

        post = post.get()
        # 삭제 가능 user 확인
        comment = Comment(
            author=g.user,
            content=data['content'],
        )
        post.comment.append(comment)
        post.save()
        return jsonify(message='댓글이 등록되었습니다.'), 200

    # 댓글 수정
    @route('<int:comment_id>', methods=['PUT'])
    @auth
    def update(self, board_name, post_id, comment_id):
        data = json.loads(request.data)

        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False)

        # 게시글 존재 여부 확인
        if not post:
            return jsonify(message='잘못된 주소입니다.'), 400

        post = post.get()
        # 삭제 가능 user 확인
        comment = post.comment[comment_id-1]
        if comment.author.id == g.user and comment.is_deleted is False:
            comment['content'] = data['content']
            post.save()
            return jsonify(message='댓글이 수정되었습니다.'), 200

        return jsonify(message='수정 권한이 없습니다.'), 401


    # 댓글 삭제
    @route('<int:comment_id>', methods=['DELETE'])
    @auth
    def delete(self, board_name, post_id, comment_id):

        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False)

        # 게시글 존재 여부 확인
        if not post:
            return jsonify(message='잘못된 주소입니다.'), 400

        post = post.get()
        # 삭제 가능 user 확인
        comment = post.comment[comment_id-1]
        if comment.author.id == g.user and comment.is_deleted is False:
            comment.is_deleted = True
            post.save()
            return jsonify(message='댓글이 삭제되었습니다.'), 200

        return jsonify(message='수정 권한이 없습니다.'), 401

