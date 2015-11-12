import redisorm.core
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

def test_persistent_prefix():
    redisorm.core.Persistent("paco")

def test_persistent_set_redis(test_redis):
    redisorm.core.Persistent("paco", r=test_redis)

class SamplePersistentObject(redisorm.core.PersistentData):
    def __init__(self, id=None, arg01="", arg02=""):
        self.id = id
        self.arg01 = arg01
        self.arg02 = arg02

def test_persistent_basic_save_and_load(test_redis):
    p = redisorm.core.Persistent("paco", r=test_redis)
    obj = SamplePersistentObject(arg01="hoge", arg02="fuga")
    p.save(obj)
    loaded = p.load(SamplePersistentObject, 0)
    assert loaded.arg01 == obj.arg01
    assert loaded.arg02 == obj.arg02

def test_persistent_save_and_load_with_int(test_redis):
    p = redisorm.core.Persistent("paco", r=test_redis)
    obj = SamplePersistentObject(arg01=3, arg02="fuga")
    p.save(obj)
    loaded = p.load(SamplePersistentObject, 0)
    assert loaded.arg01 == str(obj.arg01)
    assert loaded.arg02 == obj.arg02
