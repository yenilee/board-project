from flask_classful import FlaskView, route
from flask import jsonify

from app.models import Post
from app.serializers.post import PostListSchema,  HighRankingPostListSchema


class MainView(FlaskView):
    @route('/top10/liked-posts', methods=['GET'])
    def order_by_likes(self):
        """
        메인페이지: 좋아요 많은 글 조회 API
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
        top10_liked_posts = Post.objects(is_deleted=False).aggregate(pipeline)
        posts_list = HighRankingPostListSchema(many=True).dump(top10_liked_posts)

        return jsonify({"posts": posts_list}), 200


    @route('/top10/latest-posts', methods=['GET'])
    def order_by_latest(self):
        """
        메인페이지: 최신 글 조회 API
        :return: 최신 게시글 10개
        """
        posts = Post.objects(is_deleted=False).order_by('-created_at').limit(10)
        latest_post_list = PostListSchema(many=True).dump(posts)
        return {'posts': latest_post_list}, 200


    @route('/top10/many-comments-posts', methods=['GET'])
    def order_by_comments(self):
        """
        메인페이지: 댓글 많은 글 조회 API
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
        return {'posts': post_list}, 200