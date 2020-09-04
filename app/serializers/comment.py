from marshmallow import fields, Schema
from .user import UserSchema


class CommentCreateSchema(Schema):
    content = fields.Str(required=True)

class CommentSchema(Schema):
    id = fields.Str(required=True)
    content = fields.Str(required=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    created_at = fields.DateTime(required=True)
    like_count = fields.Integer(required=True)
    #like_count = fields.Method('calculate_like_count')
    is_replied = fields.Bool(required=True)
