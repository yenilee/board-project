from marshmallow import fields, Schema, post_load
from .serializers import UserSchema
from app.models import Post

class PostGetSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Str(dump_only=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    title = fields.Str()
    content = fields.Str()
    total_likes = fields.Method('count_likes')
    tags = fields.List(fields.String)

    def count_likes(self, obj):
        return len(obj.likes)

class PostSchema(Schema):
    id = fields.Str()
    author = fields.Nested(UserSchema)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    likes = fields.Nested(UserSchema)
    tags = fields.List(fields.Str)

    @post_load
    def make_post(self, data, **kwargs):
        post = Post(**data)
        return post


class PostCreateSchema(Schema):
    class Meta:
        fields = ['title', 'content', 'tags']


class PostUpdateSchema(PostCreateSchema):
    class Meta:
        fields = ['title', 'content', 'tags']