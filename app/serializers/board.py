from marshmallow import fields, Schema

class BoardSchema(Schema):
    id = fields.Str(required=True, uniqe=True)
    board_name = fields.Str(max_length=50, required=True)
