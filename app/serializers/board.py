from marshmallow import fields, Schema, post_load
from marshmallow.validate import Length

from app.models import Board


class BoardCategorySchema(Schema):
    name = fields.Str(required=True, validate=Length(min=1))
    id = fields.Str(required=True, validate=Length(equal=24))


class BoardCreateSchema(Schema):
    name = fields.Str(required=True, validate=Length(min=1))

    @post_load
    def make_boards(self, data, **kwargs):
        if not Board.objects(name=data['name'], is_deleted=False):
            board = Board(**data)
            return board
        return False


class BoardUpdateSchema(Schema):
    name = fields.Str(required=True, validate=Length(min=1))
