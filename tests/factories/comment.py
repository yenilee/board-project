from datetime import datetime

import factory
from factory import fuzzy
from factory.mongoengine import MongoEngineFactory

from app.models import Comment
from tests.factories.post import PostFactory
from tests.factories.user import UserFactory


class CommentFactory(MongoEngineFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = fuzzy.FuzzyText(length=10, prefix='comment_')
    created_at = factory.LazyAttribute(lambda _: datetime.utcnow())
    is_deleted = factory.LazyAttribute(lambda _: False)


class DeletedCommentFactory(CommentFactory):
    is_deleted = factory.LazyAttribute(lambda _: True)


class RepliedCommentFactory(CommentFactory):
    is_replied = factory.LazyAttribute(lambda _: True)
