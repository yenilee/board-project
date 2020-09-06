from marshmallow import fields, Schema

class UserSchema(Schema):
    id = fields.Str(required=True, uniqe=True)
    account = fields.Str(required=True, unique=True)
    password = fields.Str(required=True, load_only=True)
    created_at = fields.DateTime(required=True, load_only=True)


class BoardSchema(Schema):
    id = fields.Str(required=True, uniqe=True)
    board_name = fields.Str(max_length=50, required=True)


class CommentSchema(Schema):
    id = fields.Str(required=True)
    content = fields.Str(required=True)
    author = fields.Nested(UserSchema, dump_only=("id", "account"))
    created_at = fields.DateTime(required=True)
    like_count = fields.Integer(required=True)
    #like_count = fields.Method('calculate_like_count')
    is_replied = fields.Bool(required=True)


class PostSchema(Schema):
    id = fields.Str()
    author = fields.Nested(UserSchema)
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
