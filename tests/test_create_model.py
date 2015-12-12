import redisorm
import os
import pytest
import redis 

@pytest.fixture
def test_redis():
    port = os.environ.get("TEST_REDIS_PORT")
    r = redis.StrictRedis(port=port, decode_responses=True)
    r.ping()
    r.flushdb()
    return r

def test_create_model(test_redis):
    p = redisorm.core.Persistent("paco", r=test_redis)
    UserModel = redisorm.create_model("UserModel", id=None, name=None, nome=None, same=None, ghwaeaoigew=None)
    user = UserModel(name="John")
    p.save(user)
    assert p.load(UserModel, 0).name == "John"
