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


class CommentGetSchema(Schema):
    id = fields.Str(required=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    content = fields.Str(required=True)
    total_likes_count = fields.Method('count_likes')
    replies = fields.Method('get_replies')
    created_at = fields.DateTime(required=True)

    def count_likes(self, obj):
        return len(obj.likes)

    def get_replies(self, obj):
        return CommentGetSchema(many=True).dump(Comment.objects(replied_comment=obj.id, is_deleted=False))


class CommentSearchParamSchema(Schema):
    page = fields.Integer()


class PaginatedCommentsSchema(Schema):
    total = fields.Integer()
    items = fields.Nested(CommentGetSchema, many=True)
