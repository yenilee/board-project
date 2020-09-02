from marshmallow import fields, Schema
from .serializers import UserSchema

class PostGetSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Str(dump_only=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    title = fields.Str()
    content = fields.Str()
    total_likes = fields.Method('calculate_like_count')
    tags = fields.List(fields.String)

    def calculate_like_count(self, obj):
        return len(obj.likes)

class PostSchema(Schema):
    id = fields.Str()
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    likes = fields.Nested(UserSchema)
    tags = fields.List(fields.Str)

    class Meta:
        ordered = True


class PostCreateSchema(Schema):
    class Meta:
        fields = ['title', 'content', 'tags']


class PostUpdateSchema(PostCreateSchema):
    class Meta:
        fields = ['title', 'content', 'tags']