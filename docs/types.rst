=========
Types
=========

In the latest release, we introduced types modules that handles casting python types and redis' raw string. According to this implementation, redisorm can handles any types in addition to str. To use this, set a type on each column.

Let's get started. Consider what we defined::

  class Example(PersistentData):
      id = Column(type=types.Integer)
      message = Column(type=types.String)

And then::

  example = Example()
  example.id = "1"
  example.message = "message"
  assert isinstance(example.id, int)
  assert isinstance(example.message, str)

As you can see, all column objects are automatically casted when an assignment is execuated.

There are 4 types in module:``String``, ``Integer``, ``DateTime``, and ``Boolean``.

