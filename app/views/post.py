import json

from flask_classful import FlaskView, route
from flask          import jsonify, request, g

from app.utils      import login_required, check_board, check_post, post_validator
from app.models     import Post, Comment


class PostView(FlaskView):
    @route('', methods=['POST'])
    @login_required
    @check_board
    @post_validator
    def post(self, board_name):
        """
        게시글 생성 API
        작성자: avery
        :param board_name: 게시판 이름
        :return: message
        """
        data = json.loads(request.data)
        tag = data.get('tag')

        Post(
            board   = g.board.id,
            author  = g.user,
            title   = data['title'],
            content = data['content'],
            tag     = tag,
            post_id = Post.objects.count()+1
            ).save()

        return jsonify(message='게시글이 등록되었습니다.'), 200


    @route('/<int:post_id>', methods=['GET'])
    @check_board
    @check_post
    def get(self, board_name, post_id):
        """
        게시글 조회 API
        작성자: avery
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :return: 게시글(제목, 내용, 댓글 등)
        """
        posts_response = g.post.to_json()

        comments = Comment.objects(post=g.post.id, is_replied=False)
        reply = Comment.objects(post=g.post.id, is_replied=True)
        comment_list=[]

        for comment in comments:
            a_comment = comment.to_json()

            if reply(replied_comment=comment.id):
                a_comment['reply'] = [ reply.to_json()
                                       for reply in reply(replied_comment=comment.id)]
            comment_list.append(a_comment)

        posts_response['comments'] = comment_list
        return jsonify(posts_response), 200


    @route('/<int:post_id>', methods=['DELETE'])
    @login_required
    @check_board
    @check_post
    def delete(self, board_name, post_id):
        """
        게시글 삭제 API
        작성자: dana
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :return: message
        """
        if g.user == g.post.author.id or g.auth == True:
            g.post.update(is_deleted=True)
            return jsonify(message='삭제되었습니다.'), 200
        return jsonify(message='권한이 없습니다.'), 403


    @route('/<int:post_id>', methods=['PUT'])
    @login_required
    @check_board
    @check_post
    @post_validator
    def update(self, board_name, post_id):
        """
        게시글 수정 API
        작성자: dana
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :return: message
        """
        data = json.loads(request.data)
        tag = data.get('tag')

        # 수정 가능 user 확인
        if g.user == g.post.author.id or g.auth == True:
            g.post.update(
                title   = data['title'],
                content = data['content'],
                tag     = tag
            )
            return jsonify(message='수정되었습니다.'), 200
        return jsonify(message='권한이 없습니다.'), 403


    @route('/<int:post_id>/likes', methods=['POST'])
    @login_required
    @check_board
    @check_post
    def like_post(self, board_name, post_id):
        """
        게시글 좋아요 기능 API
        작성자: dana
        :param board_name: 게시판 이름
        :param post_id: 게시글 번호
        :return: message
        """
        post=Post.objects(likes__exact=g.user, id=g.post.id)

        # 좋아요 등록
        if not post:
            g.post.update(push__likes=g.user)
            return jsonify(message="'내가 좋아요한 게시글'에 등록되었습니다.'"), 200

        # 좋아요 취소
        g.post.update(pull__likes=g.user)
        return jsonify(message="'내가 좋아요한 게시글'에서 삭제되었습니다.'"), 200