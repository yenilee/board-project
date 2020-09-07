from datetime import datetime

import arrow as arrow
import factory
from factory import fuzzy
from factory.mongoengine import MongoEngineFactory

from app.models import Post
from tests.factories.board import BoardFactory

from tests.factories.user import UserFactory


class PostFactory(MongoEngineFactory):
    class Meta:
        model = Post

    author = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)
    title = fuzzy.FuzzyText(length=10, prefix='post_')
    content = fuzzy.FuzzyText(length=20, prefix='post_')
    created_at = factory.LazyAttribute(lambda _: datetime.utcnow()) # factory로 생성할 때 마다 새로운 date값을 부여하기 위해


