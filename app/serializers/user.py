from marshmallow import fields, Schema


class UserSchema(Schema):
    id = fields.Str(required=True, uniqe=True)
    account = fields.Str(required=True, unique=True)
    password = fields.Str(required=True, load_only=True)
    created_at = fields.DateTime(required=True, load_only=True)

