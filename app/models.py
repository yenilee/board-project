import datetime

from mongoengine import StringField, DateTimeField, ReferenceField, EmbeddedDocumentField, ListField, BooleanField, IntField
from mongoengine import Document, EmbeddedDocument


class User(Document):
    account = StringField(max_length=50, required=True, unique=True)
    password = StringField(max_length=100, required=True)
    created_at = DateTimeField(required=True, default=datetime.datetime.now)

    def to_json(self):
        return {"account": self.account}

class Tag(EmbeddedDocument):
    name = StringField(max_length=100, required=True)

class Comment(EmbeddedDocument):
    content         = StringField()
    author          = ReferenceField(User)
    likes           = ListField(ReferenceField(User))
    created_at      = DateTimeField()
    replied_comment = ReferenceField('self')

class Post(Document):
    author     = ReferenceField(User)
    board_name = ReferenceField('Board')
    title      = StringField(required=True, max_length=100)
    content    = StringField(required=True)
    created_at = DateTimeField(required=True, default=datetime.datetime.now)
    likes      = ListField(ReferenceField(User))
    tag        = ListField(EmbeddedDocumentField(Tag))
    comment    = ListField(EmbeddedDocumentField(Comment))
    is_deleted = BooleanField(required=True, default=False)
    post_id    = IntField(min_value=1)

    def to_json(self):
        return {
            'id': self.post_id,
            'author' : self.author.account,
            'title' : self.title,
            'content' : self.content,
            'created_at' : self.created_at.strftime('%Y-%m-%d-%H:%M:%S')
        }

class Board(Document):
    name = StringField(max_length=50, required=True)
    is_deleted = BooleanField(required=True, default=False)
