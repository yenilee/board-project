from flask_classful import FlaskView, route
from flask import jsonify

from app.models import Post
from app.serializers.post import PostListSchema,  HighRankingPostListSchema


class MainView(FlaskView):
    @route('/ranking/likes', methods=['GET'])
    def order_by_likes(self):
        """
        메인페이지: 좋아요 많은 글 조회 API
        작성자: avery
        :return: 좋아요 기준 게시글 10개
        """
        pipeline = [
            {"$project": {
                "board": "$board",
                "title": "$title",
                "author": "$author",
                "total_likes_count": {"$size": "$likes"}}},
            {"$sort": {"total_likes_count": -1}},
            {"$limit": 10}
        ]
        posts = Post.objects(is_deleted=False).aggregate(pipeline)
        post_list = HighRankingPostListSchema(many=True).dump(posts)

        return jsonify({"most_liked_posts": post_list}), 200


    @route('/ranking/latest', methods=['GET'])
    def order_by_latest(self):
        """
        메인페이지: 최신 글 조회 API
        작성자: dana
        :return: 최신 게시글 10개
        """
        posts = Post.objects(is_deleted=False).order_by('-created_at').limit(10)
        latest_post_list = PostListSchema(many=True).dump(posts)
        return {'latest_post_list': latest_post_list}, 200


    @route('/ranking/comments', methods=['GET'])
    def order_by_comments(self):
        """
        메인페이지: 댓글 많은 글 조회 API
        작성자: dana
        :return: 댓글 기준 게시글 10개
        """
        pipeline = [
            {"$lookup": {"from": "comment",
                         "let": {"id": "$_id"},
                         "pipeline": [
                             {"$match":
                                  {"$expr": {"$eq": ["$post", "$$id"]},
                                   "is_deleted": False}}],
                         "as": "comments"}},
            {"$project": {
                "board": "$board",
                "title": "$title",
                "author": "$author",
                "total_comments_count": {"$size": "$comments"},
                "total_likes_count": {"$size": "$likes"}}},
            {"$sort": {"total_comments_count": -1}},
            {"$limit": 10}
        ]

        posts = Post.objects(is_deleted=False).aggregate(pipeline)
        post_list = HighRankingPostListSchema(many=True).dump(posts)
        return {'post_list': post_list}, 200