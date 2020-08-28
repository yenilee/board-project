import json

from flask_classful     import FlaskView, route
from flask              import jsonify, request, g

from app.models         import Comment
from app.utils          import login_required, check_board, check_post, check_comment, comment_validator


class CommentView(FlaskView):
    @route('', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @comment_validator
    def post(self, board_name, post_id):
        """
        댓글 생성 API
        작성자: avery
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :return: message
        """
        data = json.loads(request.data)

        comment = Comment(
            post=g.post.id,
            author=g.user,
            content=data['content'],
        )
        comment.save()
        return jsonify(message='댓글이 등록되었습니다.'), 200


    @route('<comment_id>', methods=['PUT'])
    @login_required
    @check_board
    @check_post
    @comment_validator
    def update(self, board_name, post_id, comment_id):
        """
        댓글 수정 API
        작성자: avery
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :param comment_id: 댓글 objectId
        :return: message
        """
        data = json.loads(request.data)

        comment = Comment.objects(id=comment_id).get()
        if comment.author.id == g.user and comment.is_deleted is False:
            comment['content'] = data['content']
            comment.save()
            return jsonify(message='댓글이 수정되었습니다.'), 200

        return jsonify(message='수정 권한이 없습니다.'), 401


    @route('<comment_id>', methods=['DELETE'])
    @login_required
    @check_board
    @check_post
    def delete(self, board_name, post_id, comment_id):
        """
        댓글 삭제 API
        작성자: avery
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :param comment_id: 댓글 objectId
        :return: message
        """
        comment = Comment.objects(id=comment_id).get()
        if comment.author.id == g.user and comment.is_deleted is False:
            comment.is_deleted = True
            comment.save()
            return jsonify(message='댓글이 삭제되었습니다.'), 200

        return jsonify(message='수정 권한이 없습니다.'), 401


    @route('/<comment_id>/likes', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @check_comment
    def like_post(self, board_name, post_id, comment_id):
        """
        댓글 좋아요 기능 API
        작성자: dana
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :param comment_id: 댓글 objectId
        :return: message
        """
        comment = Comment.objects(likes__exact=g.user, id=comment_id)

        # 졸아요 등록
        if not comment:
            g.post.update(push__likes=g.user)
            return jsonify(message="'좋아요'가 반영되었습니다."), 200

        # 좋아요 취소
        g.comment.update(pull__likes=g.user)
        return jsonify(message="'좋아요'가 취소되었습니다."), 200


    @route('/<comment_id>/reply', methods=['POST'])
    @login_required
    @check_board
    @check_post
    @check_comment
    @comment_validator
    def post_reply(self, board_name, post_id, comment_id):
        """
        대댓글 좋아요 기능 API
        작성자: dana
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :param comment_id: 댓글 objectId
        :return: message
        """
        data = json.loads(request.data)

        reply = Comment(
            post=g.post.id,
            author=g.user,
            replied_comment=g.comment.id,
            content=data['content'],
            is_replied=True
        )
        reply.save()

        return jsonify(message='댓글이 등록되었습니다.'), 200