# redisorm
Redis Object-Relational mappings

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

All object are automatically converted into as `prefix:classname:id` style.
`prefix:Klass:__latest__` holds last insert id, and others are hashed objects composed from argument names of `__init__` functions.
