import json

from app.models import Board, Post, Comment
from flask_classful import FlaskView, route
from flask import jsonify, request, g
from app.utils import auth


class PostView(FlaskView):

    # 게시글 작성 API
    @route('', methods=['POST'])
    @auth
    def post(self, board_name):
        data = json.loads(request.data)
        tag = data.get('tag')
        
        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        Post(
            board   = board_id,
            author  = g.user,
            title   = data['title'],
            content = data['content'],
            tag     = tag,
            post_id = Post.objects.count()+1
            ).save()

        return '', 200


    # 게시글 읽기 API
    @route('/<int:post_id>', methods=['GET'])
    def get(self, board_name, post_id):

        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400

        try:
            post = Post.objects(post_id=post_id, is_deleted=False).get()
            posts_response = post.to_json()
        except:
            return jsonify(message="없는 게시물입니다."), 200

        comments = Comment.objects(post=post.id, is_replied=False)
        reply = Comment.objects(post=post.id, is_replied=True)
        comment_list=[]

        for comment in comments:
            a_comment = comment.to_json()

            if reply(replied_comment=comment.id):
                a_comment['reply'] = [ reply.to_json()
                                       for reply in reply(replied_comment=comment.id)]
            comment_list.append(a_comment)

        posts_response['comments'] = comment_list
        return jsonify(posts_response), 200


    # 게시글 삭제 API
    @route('/<int:post_id>', methods=['DELETE'])
    @auth
    def delete(self, board_name, post_id):
        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False)
        # 게시글 존재 여부 확인
        if not post:
            return jsonify(message='잘못된 주소입니다.'), 400

        # 삭제 가능 user 확인
        if g.user == post.get().author.id or g.auth == True:
            post.update(is_deleted=True)
            return jsonify(message='삭제되었습니다.'), 200
        return jsonify(message='권한이 없습니다.'), 403


    # 게시글 수정 API
    @route('/<int:post_id>', methods=['PUT'])
    @auth
    def update(self, board_name, post_id):
        data = json.loads(request.data)
        tag = data.get('tag')

        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False)
        # 게시글 존재 여부 확인
        if not post:
            return jsonify(message='잘못된 주소입니다.'), 400

        # 삭제 가능 user 확인
        if g.user == post.get().author.id or g.auth == True:
            post.update(
                title   = data['title'],
                content = data['content'],
                tag     = tag
            )
            return jsonify(message='수정되었습니다.'), 200
        return jsonify(message='권한이 없습니다.'), 403


    # 게시글 좋아요 및 취소 API
    @route('/<int:post_id>/likes', methods=['POST'])
    @auth
    def like_post(self, board_name, post_id):
        # 게시판 존재 여부 확인
        if not Board.objects(name=board_name, is_deleted=False):
            return jsonify(message='없는 게시판입니다.'), 400
        board_id = Board.objects(name=board_name, is_deleted=False).get().id

        # 게시글 존재 여부 확인
        if not Post.objects(board=board_id, post_id=post_id, is_deleted=False):
            return jsonify(message='잘못된 주소입니다.'), 400
        post = Post.objects(board=board_id, post_id=post_id, is_deleted=False).get()

        likes_user = {}
        for user_index_number in range(0,len(post.likes)):
            likes_user[post.likes[user_index_number].id] = user_index_number

        # 좋아요 누른 경우 --> 취소
        if g.user in likes_user.keys():
            user_index = likes_user[g.user]
            del post.likes[user_index]
            post.save()
            return jsonify(message="'내가 좋아요한 게시글'에서 삭제되었습니다.'"), 200

        # 좋아요 누르지 않은 경우 --> 좋아요
        post.likes.append(g.user)
        post.save()
        return jsonify(message="'내가 좋아요한 게시글'에 등록되었습니다.'"), 200