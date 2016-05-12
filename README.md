# redis-orm
Redis Object-Relational mappings

[![PyPI version](https://badge.fury.io/py/redis-orm.svg)](https://badge.fury.io/py/redis-orm)

[![Circle CI](https://circleci.com/gh/minamorl/redis-orm.svg?style=svg)](https://circleci.com/gh/minamorl/redis-orm)

## Installation

```
pip install redis-orm
```

## What is this?

```python
from redisorm.core import Client, PersistentData, Column


cl = Client("application")

class Person(PersistentData):
  id = Column()
  name = Column()

obj = Person(name="John")
cl.save(obj)
```

See [documentations](http://minamorl.github.io/redis-orm/).
## Author
minamorl
