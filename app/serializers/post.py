from flask import g

from marshmallow import fields, Schema, post_load, pre_load
from .user import UserSchema
from app.models import Post, Comment


class PostCreateSchema(Schema):
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    tags = fields.List(fields.Str)

    @post_load
    def make_post(self, data, **kwargs):
        post = Post(**data)
        return post


class PostUpdateSchema(Schema):
    title = fields.Str()
    content = fields.Str()
    tags = fields.List(fields.Str)


class PostDetailSchema(Schema):
    id = fields.Str(dump_only=True)
    author = fields.Nested(UserSchema, dump_only=("id", "email"))
    title = fields.Str()
    content = fields.Str()
    total_likes_count = fields.Method('count_likes')
    total_comments_count = fields.Method('count_comments')
    tags = fields.List(fields.String)
    created_at = fields.DateTime(dump_only=True)

    def count_likes(self, obj):
        return len(obj.likes)

    def count_comments(self, obt):
        return len(Comment.objects(post=obt.id))
