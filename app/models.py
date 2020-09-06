import datetime

from flask import g
from mongoengine import (StringField, DateTimeField, ReferenceField,
                         ListField, BooleanField, IntField, Document)


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
    likes = ListField(ReferenceField(User))
    tags = ListField(StringField())
    is_deleted = BooleanField(required=True, default=False)

    def like(self, user):
        if user not in self.likes:
            self.update(push__likes=user)

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
    likes = ListField(ReferenceField(User))
    created_at = DateTimeField(required=True, default=datetime.datetime.now)
    is_deleted = BooleanField(required=True, default=False)
    is_replied = BooleanField(required=True, default=False)

    @property
    def like_count(self):
        return len(self.likes)

    def update_comment(self, user, auth, **kwargs):
        if self.author.id == user or auth is True:
            self.update(**kwargs)
            return
        return False

    def soft_delete_comment(self, user, auth):
        if self.author.id == user or auth is True:
            self.update(is_deleted=True)
            return
        return False

    @classmethod
    def find_user_in_list(cls, comment_id, user):
        return Comment.objects(id=comment_id, likes__exact=user).count()

    def like(self, status, user):
        if status == 0:
            self.update(push__likes=user)

    def cancel_like(self, status, user):
        if status == 1:
            self.update(pull__likes=user)


    # def to_json(self):
    #     if self.is_deleted is False:
    #         return {
    #             "id": str(self.id),
    #             "author": self.author.account,
    #             "content": self.content,
    #             "created_at": self.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
    #             "likes": len(self.likes)
    #         }
    #
    #     else:
    #         return {
    #             "id": str(self.id),
    #             "author": self.author.account,
    #             "content": "삭제된 댓글입니다",
    #             "created_at": self.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
    #             "likes": len(self.likes)
    #         }
