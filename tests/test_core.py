from redisorm.core import *
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
    Persistent("paco")


def test_persistent_set_redis(test_redis):
    Persistent("paco", r=test_redis)


class SamplePersistentObject(PersistentData):
    id = Column()
    arg01 = Column(default="")
    arg02 = Column(default="")


def test_persistent_basic_save_and_load(test_redis):
    p = Persistent("paco", r=test_redis)
    obj = SamplePersistentObject(arg01="hoge", arg02="fuga")
    p.save(obj)
    loaded = p.load(SamplePersistentObject, 0)
    assert loaded.arg01 == obj.arg01
    assert loaded.arg02 == obj.arg02


def test_persistent_auto_increment_id(test_redis):
    p = Persistent("paco", r=test_redis)
    obj1 = SamplePersistentObject(arg01="hoge", arg02="fuga")
    obj2 = SamplePersistentObject(arg01="hoge", arg02="fuga")
    obj3 = SamplePersistentObject(arg01="hoge", arg02="fuga")
    p.save(obj1)
    assert obj1.id == "0"
    p.save(obj2)
    assert obj2.id == "1"
    p.save(obj3)
    assert obj3.id == "2"


def test_persistent_find_by(test_redis):
    p = Persistent("paco", r=test_redis)
    obj1 = SamplePersistentObject(arg01="hoge", arg02="fuga")
    obj2 = SamplePersistentObject(arg01="hoge", arg02="fuga")
    obj3 = SamplePersistentObject(arg01="hoge", arg02="this is target")
    p.save(obj1)
    p.save(obj2)
    p.save(obj3)
    loaded = p.find_by(SamplePersistentObject, "arg02", "this is target")
    assert loaded.arg01 == str(obj3.arg01)
    assert loaded.arg02 == obj3.arg02


def test_persistent_load_all_only_keys(test_redis):
    p = Persistent("paco", r=test_redis)
    obj1 = SamplePersistentObject(arg01="hoge", arg02="fuga")
    obj2 = SamplePersistentObject(arg01="hoge", arg02="reversed")
    obj3 = SamplePersistentObject(arg01="hoge", arg02="this is target")
    p.save(obj1)
    p.save(obj2)
    p.save(obj3)
    loaded = p.load_all_only_keys(SamplePersistentObject, "arg02")
    assert obj1.arg02 == next(loaded)
    assert obj2.arg02 == next(loaded)
    assert obj3.arg02 == next(loaded)


def test_persistent_load_all_only_keys_reverse_true(test_redis):
    p = Persistent("paco", r=test_redis)
    obj1 = SamplePersistentObject(arg01="hoge", arg02="fuga")
    obj2 = SamplePersistentObject(arg01="hoge", arg02="reversed")
    obj3 = SamplePersistentObject(arg01="hoge", arg02="this is target")
    p.save(obj1)
    p.save(obj2)
    p.save(obj3)
    loaded = p.load_all_only_keys(SamplePersistentObject, "arg02", reverse=True)
    assert obj3.arg02 == next(loaded)
    assert obj2.arg02 == next(loaded)
    assert obj1.arg02 == next(loaded)


def test_delete(test_redis):
    p = Persistent("paco", r=test_redis)
    obj = SamplePersistentObject(arg01="hoge", arg02="fuga")
    p.save(obj)
    assert p.load(SamplePersistentObject, 0) != None
    p.delete(obj)
    assert p.load(SamplePersistentObject, 0) == None


def test_delete2(test_redis):
    p = Persistent("paco", r=test_redis)
    obj = SamplePersistentObject(arg01="hoge", arg02="fuga")
    obj2 = SamplePersistentObject(arg01="hoge", arg02="fuga")
    p.save(obj)
    p.save(obj2)
    p.delete(obj)
    assert len(list(p.load_all(SamplePersistentObject))) == 2
    assert list(p.load_all(SamplePersistentObject))[0] == None
