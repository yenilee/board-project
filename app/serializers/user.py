import bcrypt

from marshmallow import fields, Schema, post_load
from app.models import User


class UserSchema(Schema):
    id = fields.Str()
    account = fields.Str(required=True, unique=True)
    password = fields.Str(required=True, load_only=True)
    created_at = fields.DateTime(load_only=True)

    @post_load
    def check_users(self, data, **kwargs):
        if not User.objects(account=data['account']):
            return False
        else:
            return User.objects(account=data['account']).get()


class UserCreateSchema(Schema):
    account = fields.Str(required=True, unique=True)
    password = fields.Str(required=True, load_only=True)

    @post_load
    def make_users(self, data, **kwargs):
        if not User.objects(account=data['account']):
            password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            data['password'] = password
            user = User(**data)
            return user
        return False

