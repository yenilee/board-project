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
        # if Board.objects(name=data['name'], is_deleted=False):
        #     return {'message': '이미 등록된 게시판입니다.'}, 409
        board = Board(**data)
        return board