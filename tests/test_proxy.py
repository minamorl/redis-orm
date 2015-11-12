import datetime
import redisorm.core
from redisorm.proxy import DatetimeProxy, BooleanProxy, PersistentProxy
import redis
import pytest
import os


@pytest.fixture
def test_redis():
    port = os.environ.get("TEST_REDIS_PORT")
    r = redis.StrictRedis(port=port, decode_responses=True)
    r.ping()
    r.flushdb()
    return r


def test_datetime_proxy():
    now = datetime.datetime.now()
    dt = DatetimeProxy(now)
    assert now == dt
    assert str(dt) == str(dt.retrive())


def test_boolean_proxy():
    assert "False" == str(BooleanProxy(False))
    assert "False" == str(BooleanProxy("False"))
    assert False == BooleanProxy("False").retrive()
    assert True == BooleanProxy("True").retrive()


class SampleModel(redisorm.core.PersistentData):

    def __init__(self, id=None, child=None):
        self.id = id
        self.child = PersistentProxy(child)


class SampleChildModel(redisorm.core.PersistentData):

    def __init__(self, id=None):
        self.id = id


def test_persistent_proxy(test_redis):
    p = redisorm.core.Persistent("paco", r=test_redis)
    child = SampleChildModel()
    p.save(child)
    assert str(child) == "0"

def test_persistent_proxy(test_redis):
    p = redisorm.core.Persistent("paco", r=test_redis)
    child = SampleChildModel()
    p.save(child)

    parent = SampleModel(child=child)
    p.save(parent)

    parent.child.retrive(SampleChildModel, p).id == "0"
