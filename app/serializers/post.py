from flask import g

from marshmallow import fields, Schema, post_load, validates_schema
from .user import UserSchema
from app.models import Post

class PostGetSchema(Schema):
    id = fields.Str(dump_only=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    title = fields.Str()
    content = fields.Str()
    total_likes = fields.Method('count_likes')
    tags = fields.List(fields.String)

    def count_likes(self, obj):
        return len(obj.likes)

    def validate_request(self, data, **kwargs):
        errors = {}


class PostSchema(Schema):
    id = fields.Str()
    author = fields.Nested(UserSchema)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    likes = fields.Nested(UserSchema)
    tags = fields.List(fields.Str)

    @post_load
    def make_post(self, data, **kwargs):
        data['author'] = g.user
        data['board'] = g.board.id
        post = Post(**data)
        return post

class PostUpdateSchema(PostSchema):
    title = fields.Str()
    content = fields.Str()
    tags = fields.List(fields.Str)
