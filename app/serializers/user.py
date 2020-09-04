from marshmallow import fields, Schema

class UserSchema(Schema):
    account = fields.Str(required=True, unique=True)
    password = fields.Str(required=True)
    created_at = fields.DateTime()
