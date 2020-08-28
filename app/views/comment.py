import json

from flask_classful     import FlaskView, route
from flask              import jsonify, request, g
from marshmallow        import ValidationError

from app.models         import Comment
from app.utils          import login_required, check_board, check_post, check_comment
from app.serializers    import CommentSchema



class CommentView(FlaskView):

    # 댓글 생성
    @route('', methods=['POST'])
    @login_required
    @check_board
    @check_post
    def post(self, board_name, post_id):
        data = json.loads(request.data)

        try:
            CommentSchema().load(data)
        except ValidationError as err:
            return jsonify (err.messages), 422

        comment = Comment(
            post=g.post.id,
            author=g.user,
            content=data['content'],
        )
        comment.save()
        return jsonify(message='댓글이 등록되었습니다.'), 200

    # 댓글 수정
    @route('<comment_id>', methods=['PUT'])
    @login_required
    @check_board
    @check_post
    def update(self, board_name, post_id, comment_id):
        data = json.loads(request.data)

        try:
            CommentSchema().load(data)
        except ValidationError as err:
            return jsonify (err.messages), 422

        comment = Comment.objects(id=comment_id).get()
        if comment.author.id == g.user and comment.is_deleted is False:
            comment['content'] = data['content']
            comment.save()
            return jsonify(message='댓글이 수정되었습니다.'), 200

        return jsonify(message='수정 권한이 없습니다.'), 401


    # 댓글 삭제
    @route('<comment_id>', methods=['DELETE'])
    @login_required
    @check_board
    @check_post
    def delete(self, board_name, post_id, comment_id):

        # 삭제 가능 user 확인
        comment = Comment.objects(id=comment_id).get()
        if comment.author.id == g.user and comment.is_deleted is False:
            comment.is_deleted = True
            comment.save()
            return jsonify(message='댓글이 삭제되었습니다.'), 200

        return jsonify(message='수정 권한이 없습니다.'), 401


    # 댓글 좋아요 및 취소 API
    @route('/<comment_id>/likes', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @check_comment
    def like_post(self, board_name, post_id, comment_id):

        likes_user = {}
        for user_index_number in range(0,len(g.comment.likes)):
            likes_user[g.comment.likes[user_index_number].id] = user_index_number

        # 좋아요 누른 경우 --> 취소
        if g.user in likes_user.keys():
            user_index = likes_user[g.user]
            del g.comment.likes[user_index]
            g.comment.save()
            return jsonify(message="'좋아요'가 취소되었습니다."), 200

        # 좋아요 누르지 않은 경우 --> 좋아요
        g.comment.likes.append(g.user)
        g.comment.save()
        return jsonify(message="'좋아요'가 반영되었습니다."), 200


    # 대댓글 생성 API
    @route('/<comment_id>/reply', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @check_comment
    def post_reply(self, board_name, post_id, comment_id):
        data = json.loads(request.data)

        try:
            CommentSchema().load(data)
        except ValidationError as err:
            return jsonify (err.messages), 422

        reply = Comment(
            post=g.post.id,
            author=g.user,
            replied_comment=g.comment.id,
            content=data['content'],
            is_replied=True
        )
        reply.save()

        return jsonify(message='댓글이 등록되었습니다.'), 200