import factory
from factory.mongoengine import MongoEngineFactory

from app.models import User

class UserFactory(MongoEngineFactory):
    class Meta:
        model = User

    account = factory.Faker('name')
    password = factory.Faker('password')


    @classmethod
    def create_with_user(cls, **kwargs):
        user = UserFactory.create(**kwargs)
        return user