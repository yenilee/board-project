import factory
from factory import fuzzy
from factory.mongoengine import MongoEngineFactory

from app.models import Board


class BoardFactory(MongoEngineFactory):
    class Meta:
        model = Board

    name = fuzzy.FuzzyText(length=10, prefix='board_')
    is_deleted = factory.LazyAttribute(lambda _: False)

class DeletedBoardFactory(BoardFactory):
    is_deleted = factory.LazyAttribute(lambda _: True) # 임의의 값을 넣을때