# redis-orm
Redis Object-Relational mappings

[![Circle CI](https://circleci.com/gh/minamorl/redis-orm.svg?style=svg)](https://circleci.com/gh/minamorl/redis-orm)

## Installation

```
pip install redis-orm
```

Do install carefully because `pip install redisorm` installs other package.

## What is this?

Redis is fast, reliable, very simple key-value store, but redis-py's interface are not intutibe.

***redisorm(redis-orm)*** provides orm like feature. Like pickle module, it makes your class instances persistent in a beautiful way.

```python
import redisorm.core


p = redisorm.core.Persistent("prefix")
save = p.save
load = p.load

class Klass(redisorm.core.PersistentData):
  self __init__(self, id=None, name=None, ):
    self.id = id
    self.name = name
   
#Save stuffs
k1 = Klass(name="foo")
save(k1)
print(k1.id)
k2 = Klass(name="bar")
save(k2)
print(k2.id)

#Load
j1 = load(Klass, 0)
print(j1.name)
j2 = load(Klass, 1)
print(j2.name)
```

Results:
```
0
1
foo
bar
```

OMG! What is happen? Let's look inside of redis.
```
% redis-cli
127.0.0.1:6379> keys *
1) "prefix:Klass:1"
2) "prefix:Klass:0"
3) "prefix:Klass:__latest__"
```

All object are automatically converted into str, and all `id` is managed by `prefix:classname:__latest__` value.

By default, `prefix:Klass:__latest__` holds last insert id, and others are hashed objects composed from argument names of `__init__` functions.

## Restriction

All kwargs of `__init__` function which derivered `PersistentData` classes must be string representable except `self`, and they must have default values.

However, in a real world, we have to handle vary datatypes such as DateTime, int, Boolean, and so on. If you need to handle those types without thinking about cast, you can use proxy objects.

## Proxies


### DatetimeProxy
```python
import datetime
import redisorm.core
from redisorm.proxy import DatetimeProxy

p = redisorm.core.Persistent("example")

class SampleObject(redisorm.core.PersistentData):
  def __init__(self, created_at=None, id=None):
    self.id = id
    self.created_at = DatetimeProxy(created_at) or DatetimeProxy(datetime.datetime.now())

p.save(SampleObject())
obj = p.load(SampleObject, 0)

print(type(obj.created_at))
# Retrive as 'actual' data type.
print(type(obj.created_at.retrive()))

# Results are:
# <class 'redisorm.proxy.DatetimeProxy'>
# <class 'datetime.datetime'>
```

## Advanced Proxy Receipe

### hasMany (or belongsTo)

```python
class User(redisorm.core.PersistentData):
  def __init__(self, id=None, user=None):
    self.id = id
    self.memo_list = PersistentListProxy()
  
  def get_all_memo():
    return self.memo_list.retrive()

class Memo(redisorm.core.PersistentData):
  def __init__(self, id=None, memor=None):
    self.id = id
    self.author = PersistentProxy()

  def get_author():
    return self.author.retrive()
```
