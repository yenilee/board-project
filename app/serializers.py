from marshmallow import fields, Schema

class UserSchema(Schema):
    account     = fields.Str(required=True, unique=True)
    password    = fields.Str(required=True)
    created_at  = fields.DateTime()

class BoardSchema(Schema):
    name = fields.Str(max_length=50, required=True)

class CommentSchema(Schema):
    content     = fields.Str(required=True)

class PostSchema(Schema):
    author = fields.Nested(UserSchema)
    board = fields.Nested(BoardSchema)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    likes = fields.Nested(UserSchema)
    tag = fields.List(fields.Str)

    class Meta:
        ordered = True