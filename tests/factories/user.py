import factory
from factory.mongoengine import MongoEngineFactory

from app.models import User
from factory import fuzzy


class UserFactory(MongoEngineFactory):
    class Meta:
        model = User

    account = factory.Faker('name')
    password = factory.Faker('password')
    master_role = factory.LazyAttribute(lambda _: False)


class MasterUserFactory(UserFactory):
    master_role = factory.LazyAttribute(lambda _: True)


class FakeTokenFactory(MongoEngineFactory):
    token = fuzzy.FuzzyText(length=100)
