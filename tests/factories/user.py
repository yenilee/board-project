import factory
from factory.mongoengine import MongoEngineFactory

from app.models import User

class UserFactory(MongoEngineFactory):
    class Meta:
        model = User

    account = factory.Faker('name')
    password = factory.Faker('password')
