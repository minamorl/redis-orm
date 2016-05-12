============================
Getting Started
============================

Download
===================

Install via pip (recommended)
-------------------------------------

You can install redis-orm using pip

.. code-block:: bash

  $ pip install redis-orm

Install manually
-------------------------------------

.. code-block:: bash

  $ git clone https://github.com/minamorl/redis-orm/
  $ cd redis-orm && python setup.py install


Create a model
====================

To create a model, you have to create a class that inherits 
``redisorm.Model``. Below is an example::

  from redisorm import Model, Column

  class Person(Model):
      id = Column()
      name = Column()
      address = Column()


Or you can simply use ``redisorm.create_model`` helper to create
a class::

  from redisorm import Model, Column

  Person = redisorm.create_model("Person",
      id = Column(),
      name = Column(),
      address = Column()
  )

Make sure that `id` column is set. This is important because
redis-orm looks up all instance with ids. If `id` column is missing,
redis-orm will be not able to find your models. This is important behavior.

Save and Load
=========================

Create an instance
---------------------------


You can create an instance from a Model-derived class.

::

  person = Person(name="John")

Usually, you should not set the `id` column.


Save an instance
---------------------------

First, you shoud create an instance of ``redisorm.Client``::

  import redisorm
  client = redisorm.Client()
  
By the default, redis-orm creates an instance of redis with a
default values. You can also pass a custom redis instance::

  import redis

  r = redis.StrictRedis(port=32123, decode_responses=True)
  redisorm.Client(r=r)

Then::

  client.save(person)
  
That's it.

Loading from redis
-----------------------------


``Client.load_all`` yields all instances from existing data in Redis.

::

  for person from client.load_all(Person):
      print(person.name)

Or you can specify the id to ``Cient.load`` and get the instance::

  person = client.load(Person, 0)
  print(person.name)
