from marshmallow import fields, Schema
from .serializers import UserSchema

class PostGetSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Str(dump_only=True)
    author = fields.Nested(UserSchema)
    title = fields.Str()
    content = fields.Str()
    total_likes = fields.Method('calculate_like_count')
    tags = fields.List(fields.String)

    def calculate_like_count(self, obj):
        return len(obj.likes)