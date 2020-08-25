from marshmallow import fields, Schema, validates_schema, ValidationError

class UserSchema(Schema):
    account = fields.Str(required=True)
    password = fields.Str(required=True)
    created_at = fields.DateTime()

class BoardSchema(Schema):
    name = fields.Str(max_length=50, required=True)