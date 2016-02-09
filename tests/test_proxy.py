import datetime
import redisorm
from redisorm.core import Column
from redisorm.proxy import DatetimeProxy, BooleanProxy, PersistentProxy, IntProxy, PersistentListProxy
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


def test_int_proxy():
    i = 3
    proxied = IntProxy(i)
    assert i == proxied
    assert str(i) == str(proxied)
    assert i == proxied.retrive()


def test_boolean_proxy():
    assert "False" == str(BooleanProxy(False))
    assert "False" == str(BooleanProxy("False"))
    assert False == BooleanProxy("False").retrive()
    assert True == BooleanProxy("True").retrive()


class SampleModel(redisorm.core.PersistentData):

    id = Column()
    child = Column(PersistentProxy)


class SampleChildModel(redisorm.core.PersistentData):

    id = redisorm.core.Column()


def test_persistent_proxy(test_redis):
    p = redisorm.core.Persistent("paco", r=test_redis)
    child = SampleChildModel()
    p.save(child)
    assert str(child) == "0"

    parent = SampleModel(child=child)
    p.save(parent)

    assert parent.child.retrive(SampleChildModel, p).id == "0"


def test_persistent_list_proxy(test_redis):
    p = redisorm.core.Persistent("paco", r=test_redis)
    obj = PersistentListProxy([])
    assert obj == []


def test_persistent_list_proxy_check_retrive_chain(test_redis):
    p = redisorm.core.Persistent("paco", r=test_redis)
    obj = PersistentListProxy([])
    a = IntProxy("6")
    b = IntProxy(4)

    obj.append(a)
    obj.append(b)
    assert obj.retrive() == [6, 4]
    assert obj != [6, 4]
    assert obj == ["6", 4]
