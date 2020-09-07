from marshmallow import fields, Schema, post_load

from .user import UserSchema
from app.models import Comment

class CommentCreateSchema(Schema):
    content = fields.Str(required=True)

    @post_load
    def make_comment(self, data, **kwargs):
        comment = Comment(**data)
        return comment

class CommentUpdateSchema(CommentCreateSchema):
    class Meta:
        fields = ['content']


class CommentSchema(Schema):
    id = fields.Str(required=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    content = fields.Str(required=True)
    total_likes_count = fields.Method('count_likes')
    created_at = fields.DateTime(required=True)
    is_deleted = fields.Bool(required=True)

    def count_likes(self, obj):
        return len(obj.likes)

class CommentGetSchema(CommentSchema):
    is_replied = fields.Bool(required=True)

    class Meta:
        exclude = ("is_deleted",)


class PaginatedCommentsSchema(Schema):
    total = fields.Integer()
    items = fields.Nested(CommentSchema, many=True)