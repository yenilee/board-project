import mongoengine
from app.config import TestConfig

mongoengine.connect(host=TestConfig.MONGO_URI)
mongoengine.disconnect()
