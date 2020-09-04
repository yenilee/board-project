from marshmallow import fields, Schema


class CommentCreateSchema(Schema):
    content = fields.Str(required=True)
