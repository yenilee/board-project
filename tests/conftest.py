import mongoengine
from app.config import TestConfig

mongoengine.connect(host=TestConfig.MONGO_URI)

def test_simple_test():
  assert 1

mongoengine.disconnect()