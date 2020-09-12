from marshmallow import fields, Schema, post_load
from marshmallow.validate import Length

from .user import UserSchema
from app.models import Comment


class CommentCreateSchema(Schema):
    content = fields.Str(required=True, validate=Length(min=1))

    @post_load
    def make_comment(self, data, **kwargs):
        comment = Comment(**data)
        return comment


class CommentUpdateSchema(Schema):
    content = fields.Str(required=True, validate=Length(min=1))


class CommentSchema(Schema):
    id = fields.Str(required=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    content = fields.Str(required=True)
    total_likes_count = fields.Method('count_likes')
    created_at = fields.DateTime(required=True)
    is_reply = fields.Bool(required=True)

    def count_likes(self, obj):
        return len(obj.likes)


class CommentSearchParamSchema(Schema):
    page = fields.Integer()


class PaginatedCommentsSchema(Schema):
    total = fields.Integer()
    items = fields.Nested(CommentSchema, many=True)

class ReplySchema(CommentSchema):
    fields = ["id", "author", "content", "created_at"]

class CommentListWithReplySchema(CommentSchema):
    fields = ["id", "author", "content", "total_likes_count", "created_at"]