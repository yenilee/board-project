import datetime
from flask_mongoengine import Document
from mongoengine import (StringField, DateTimeField, ReferenceField,
                         ListField, BooleanField)


class User(Document):
    account = StringField(max_length=50, required=True, unique=True)
    password = StringField(max_length=100, required=True)
    created_at = DateTimeField(required=True, default=datetime.datetime.now)
    master_role = BooleanField(required=True, default=False)


class Board(Document):
    name = StringField(max_length=50, required=True)
    is_deleted = BooleanField(required=True, default=False)


class Post(Document):
    author = ReferenceField(User)
    board = ReferenceField(Board)
    title = StringField(max_length=100)
    content = StringField()
    created_at = DateTimeField(required=True, default=datetime.datetime.now)
    likes = ListField(StringField())
    tags = ListField(StringField())
    is_deleted = BooleanField(required=True, default=False)

    def like(self, user):
        if str(user) not in self.likes:
            self.update(push__likes=str(user))

    def cancel_like(self, user):
        if str(user) in self.likes:
            self.update(pull__likes=str(user))

    def soft_delete(self, login_user_id, login_user_auth):
        if login_user_id == self.author.id or login_user_auth == True:
            self.update(is_deleted=True)
            return True

    def make_updates(self, login_user_id, login_user_auth, post):
        if login_user_id == self.author.id or login_user_auth == True:
            self.update(**post)
            return True


class Comment(Document):
    post = ReferenceField(Post)
    author = ReferenceField(User)
    reply = ReferenceField('self')
    content = StringField()
    likes = ListField(StringField())
    created_at = DateTimeField(required=True, default=datetime.datetime.now)
    is_deleted = BooleanField(required=True, default=False)
    is_replied = BooleanField(required=True, default=False)

    @property
    def like_count(self):
        return len(self.likes)

    def make_updates(self, user, auth, data):
        if self.author.id == user or auth is True:
            self.update(**data)
            return
        return False

    def soft_delete(self, user, auth):
        if self.author.id == user or auth is True:
            self.update(is_deleted=True)
            return
        return False

    def like(self, user):
        if str(user) not in self.likes:
            self.update(push__likes=str(user))

    def cancel_like(self, user):
        if str(user) in self.likes:
            self.update(pull__likes=str(user))
