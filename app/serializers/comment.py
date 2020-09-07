from marshmallow import fields, Schema

from .user import UserSchema


class CommentCreateSchema(Schema):
    content = fields.Str(required=True)


class CommentUpdateSchema(Schema):
    content = fields.Str(required=True)


class CommentSchema(Schema):
    id = fields.Str(required=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    content = fields.Str(required=True)
    number_of_likes = fields.Method('calculate_like_count')
    created_at = fields.DateTime(required=True)
    is_deleted = fields.Bool(required=True)

    def calculate_like_count(self, obj):
        return len(obj.likes)

class CommentGetSchema(CommentSchema):
    is_replied = fields.Bool(required=True)

    class Meta:
        exclude = ("is_deleted",)


class PaginatedCommentsSchema(Schema):
    total = fields.Integer()
    items = fields.Nested(CommentSchema, many=True)