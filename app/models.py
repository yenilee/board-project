from mongoengine import StringField, DateTimeField, ReferenceField, EmbeddedDocumentField, ListField
from mongoengine import Document, EmbeddedDocument

class User(Document):
    account = StringField(max_length=50, required=True, unique=True)
    password = StringField(max_length=100)
    created_at = DateTimeField()

    def to_json(self):
        return {"account": self.account}

class Board(Document):
    name = StringField(max_length=50, required=True)
    post = ListField(EmbeddedDocumentField(Post))

class Tag(EmbeddedDocument):
    name = StringField(max_length=100, required=True)

class Comment(EmbeddedDocument):
    content         = StringField()
    author          = ReferenceField(User)
    likes           = ListField(ReferenceField(User))
    created_at      = DateTimeField()
    replied_comment = ReferenceField('self')

class Post(EmbeddedDocument):
    author     = ReferenceField(User)
    title      = StringField(max_length=100)
    content    = StringField()
    created_at = DateTimeField()
    board_name = ReferenceField(Board)
    likes      = ListField(ReferenceField(User))
    tag        = ListField(EmbeddedDocumentField(Tag))
    comment    = ListField(EmbeddedDocumentField(Comment))


