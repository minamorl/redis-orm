import pytest
import os
import redis

from redisorm import Persistent, PersistentData, Column, types


@pytest.fixture
def test_redis():
    port = os.environ.get("TEST_REDIS_PORT")
    r = redis.StrictRedis(port=port, decode_responses=True)
    r.ping()
    r.flushdb()
    return r


def test_column_casts_type_correctly(test_redis):
    class Example(PersistentData):
        id = Column()
        created_at = Column(types.DateTime, primary_key=True)
    example = Example(id=0, created_at='2011-11-03 18:21:26')
    assert not isinstance(example.created_at, types.DateTime)
    example.created_at = types.DateTime('2011-11-03 18:21:26')
    assert not isinstance(example.created_at, types.DateTime)
    example.created_at = '2011-11-03 18:21:28'
    assert not isinstance(example.created_at, types.DateTime)
    assert example.created_at == types.DateTime('2011-11-03 18:21:28').obj


@pytest.mark.xfail
def test_persistent_data_has_only_one_primary_key(test_redis):
    class Example(PersistentData):
        id = Column()
        created_at = Column(types.DateTime, primary_key=True)
        created_at2 = Column(types.DateTime, primary_key=True)


def test_persistent_data_holds_primary_key(test_redis):
    class Example1(PersistentData):
        id = Column()
        created_at = Column(types.DateTime, primary_key=True)
    assert Example1._primary_key == "created_at"

    class Example2(PersistentData):
        id = Column()
        created_at = Column(types.DateTime)
    assert Example2._primary_key is None


def test_persistent_data_save_and_load_with_primary_key(test_redis):
    import datetime

    class Example(PersistentData):
        id = Column()
        created_at = Column(types.DateTime, primary_key=True, default="2016-05-08 00:00:00")
    p = Persistent("example", r=test_redis)
    example = Example()
    p.save(example)
    assert test_redis.lrange("example:Example:__sorted__", 0, -1) == ["0"]
    p.save(Example(created_at="2016-05-08 01:00:00"))
    p.save(Example(created_at="2016-05-08 02:00:00"))
    p.save(Example(created_at="2016-05-08 05:00:00"))
    p.save(Example(created_at="2016-05-08 04:00:00"))
    assert test_redis.lrange("example:Example:__sorted__", 0, -1) == ["0", "1", "2", "4", "3"]
    assert [str(item.id) for item in p.load_all(Example)] == ["0", "1", "2", "4", "3"]
    assert [item for item in p.load_all_only_keys(Example, "id")] == ["0", "1", "2", "4", "3"]
