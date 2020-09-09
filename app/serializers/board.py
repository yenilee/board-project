from marshmallow import fields, Schema

class BoardSchema(Schema):
    board_name = fields.Str(max_length=50, required=True)
