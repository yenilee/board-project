from marshmallow import fields, Schema, validates_schema, ValidationError

class UserSchema(Schema):
    account = fields.Str(required=True)
    password = fields.Str(required=True)
    created_at = fields.DateTime()
