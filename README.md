# redis-orm
Redis Object-Relational mappings

[![PyPI version](https://badge.fury.io/py/redis-orm.svg)](https://badge.fury.io/py/redis-orm)

[![Circle CI](https://circleci.com/gh/minamorl/redis-orm.svg?style=svg)](https://circleci.com/gh/minamorl/redis-orm)

## Installation

```
pip install redis-orm
```

## What is this?

Redis is a fast, reliable, very simple key-value store.  
But there's a problem: redis-py's interface is not well-designed.

***redisorm(redis-orm)*** provides orm-like feature. Like pickle module, it makes your class instances persistent in a beautiful way.

```python
from redisorm.core import Persistent, PersistentData, Column


p = Persistent("prefix")

class Klass(PersistentData):
  id = Column()
  name = Column()
   

#Save stuffs
k1 = Klass(name="foo")
p.save(k1)
print(k1.id)
k2 = Klass(name="bar")
p.save(k2)
print(k2.id)

#Load
j1 = p.load(Klass, 0)
print(j1.name)
j2 = p.load(Klass, 1)
print(j2.name)
```

Result:
```
0
1
foo
bar
```

OMG! What is happening? Let's look inside into redis.
```
% redis-cli
127.0.0.1:6379> keys *
1) "prefix:Klass:1"
2) "prefix:Klass:0"
3) "prefix:Klass:__latest__"
```

All object are automatically converted into `str`, and all `id` is managed by `prefix:classname:__latest__` value.

By default, `prefix:Klass:__latest__` holds last inserted id, and others are hashed objects composed from argument names of `__init__` functions.

## Types

In the latest release, we introduced `types` modules. According to this implementation, redisorm can set a *type* on each column.

Let's get started. Consider what we defined:
```python
class Example(redisorm.PersistentData):
  id = Column()
  message = Column(type=redisorm.types.String)
  created_at = Column(type=redisorm.types.DateTime, default=lambda: datetime.datetime.now())
```

```
example = Example()

# returns datetime object, which value is defined as a creation time.
example.created_at 
```



## Proxies[obsolated]

This module support has been dropped since latest major release of redis-orm.
Use new `redisorm.types` moduleds instead of this.

### Restriction

All kwargs of `__init__` function which derived from `PersistentData` classes must be string representable except for `self`, and they also must have default values.

However, in a real world, we have to handle various datatypes such as `DateTime`, `int`, `Boolean`, and so on. If you need to handle those types without thinking about casting, you can use proxy objects.

### DatetimeProxy
```python
import datetime
import redisorm.core
from redisorm.core import Core
from redisorm.proxy import DatetimeProxy

p = redisorm.core.Persistent("example")

class SampleObject(redisorm.core.PersistentData):
  created_at = Column() 
  id = Column()

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

There are several proxies:

- DatetimeProxy
- IntProxy
- BooleanProxy
- PersistentProxy
- PersistentListProxy

## Advanced Proxy Receipe: hasMany (or belongsTo) relationships 

**redisorm** represents object relationships in pythonic way. Look at this example:

```python
persistent = redisorm.core.Persistent("example")

class User(redisorm.core.PersistentData):
  id = redisorm.core.Column()
  memo_list = redisorm.core.Column()

  def __init__(self, id=None, user=None):
    self.id = id
    self.memo_list = PersistentListProxy()
  
  def get_all_memo():
    return self.memo_list.retrive(Memo, persistent)

class Memo(redisorm.core.PersistentData):
  def __init__(self, id=None, author=None):
    self.id = id
    self.author = PersistentProxy()

  def get_author():
    return self.author.retrive(Author, persistent)
```

In this example, User has many Memo. Memo can also possess an author. 

redisorm do not generate any magic method implicitly. You can implement getters explicitly, by your comfortable way.


## Author
minamorl
