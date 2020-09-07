from flask import g

from marshmallow import fields, Schema, post_load
from .user import UserSchema
from app.models import Post, Comment

# 조회용
class PostGetSchema(Schema):
    id = fields.Str(dump_only=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    title = fields.Str()
    content = fields.Str()
    total_likes = fields.Method('count_likes')
    total_comments = fields.Method('count_comments')
    tags = fields.List(fields.String)
    created_at = fields.DateTime(dump_only=True)

    def count_likes(self, obj):
        return len(obj.likes)

    def count_comments(self, obt):
        return len(Comment.objects(post=obt.id))


class PostSchema(Schema):
    id = fields.Str()
    author = fields.Nested(UserSchema)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    likes = fields.Nested(UserSchema)
    tags = fields.List(fields.Str)

# 수정
class PostUpdateSchema(PostSchema):
    class Meta:
        fields = ['title', 'content', 'tags']

# 생성용
class PostCreateSchema(PostSchema):
    class Meta:
        fields = ['title', 'content', 'tags']

    @post_load
    def make_post(self, data, **kwargs):
        data['author'] = g.user
        data['board'] = g.board.id
        post = Post(**data)
        return post
