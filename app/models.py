import datetime

from mongoengine import (StringField, DateTimeField, ReferenceField,
                         ListField, BooleanField, IntField, Document)


class User(Document):
    account = StringField(max_length=50, required=True, unique=True)
    password = StringField(max_length=100, required=True)
    created_at = DateTimeField(required=True, default=datetime.datetime.now)
    master_role = BooleanField(required=True, default=False)

    def to_json(self):
        return {"account": self.account}


class Board(Document):
    name = StringField(max_length=50, required=True)
    is_deleted = BooleanField(required=True, default=False)


class Post(Document):
    author = ReferenceField(User)
    board = ReferenceField(Board)
    title = StringField(required=True, max_length=100)
    content = StringField(required=True)
    created_at = DateTimeField(required=True, default=datetime.datetime.now)
    likes = ListField(ReferenceField(User))
    tag = ListField()
    is_deleted = BooleanField(required=True, default=False)
    post_id = IntField(min_value=1)

    def like(self, user):

        if not user in self.likes:
            self.update(push__likes=user)

    def to_json(self):
        return {
            'id': self.post_id,
            'author': self.author.account,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
            'tag': self.tag,
            'likes': len(self.likes),
            # 'comments': [{"comment_id": str(comment.id),
            #               "name": comment.author.account,
            #               "content": comment.content,
            #               "created_at": comment.created_at.strftime('%Y-%m-%d-%H:%M:%S')}
            #              for comment in Comment.objects(post=self.id, is_deleted=False).all()]
        }

    def to_json_list(self):
        return {
            'board': self.board.name,
            'id': self.post_id,
            'author': self.author.account,
            'title': self.title,
            'created_at': self.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
            'likes': len(self.likes),
            'comments': Comment.objects(post=self.id, is_deleted=False).count()
            # 'tag' : self.tag
        }


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

    def to_json(self):
        if self.is_deleted is False:
            return {
                "id": str(self.id),
                "author": self.author.account,
                "content": self.content,
                "created_at": self.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
                "likes": len(self.likes)
            }

        else:
            return {
                "id": str(self.id),
                "author": self.author.account,
                "content": "삭제된 댓글입니다",
                "created_at": self.created_at.strftime('%Y-%m-%d-%H:%M:%S'),
                "likes": len(self.likes)
            }
