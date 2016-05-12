=====================
Getting Started
=====================

Redis is a fast, reliable, very simple key-value store. But there's a problem: redis-py's interface is not well-designed.

**redisorm(redis-orm)** provides orm-like feature. Like pickle module, it makes your class instances persistent in a beautiful way::

    from redisorm import Client, PersistentData, Column


    p = Client("prefix")

    class Klass(PersistentData):
      id = Column()
      name = Column()

As we can see, to define a model is very simple. This is how to use it::

    k1 = Klass(name="foo")
    k2 = Klass(name="bar")
    p.save(k1)
    p.save(k2)
    j1 = p.load(Klass, 0)
    j2 = p.load(Klass, 1)

What is happening? Let's look inside into redis::

    % redis-cli
    127.0.0.1:6379> keys *
    1) "prefix:Klass:1"
    2) "prefix:Klass:0"
    3) "prefix:Klass:__latest__"

All object are automatically converted into str, and all id is managed by prefix:classname:__latest__ value.

By default, prefix:Klass:__latest__ holds last inserted id, and others are hashed objects composed from argument names of __init__ function.
