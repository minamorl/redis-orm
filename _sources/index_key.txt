======================
Index Key
======================

Index key is a new feature for sorting user data. Now redis-orm performs like SQL. If index key is set, Redis-ORM automatically creates special __sorted__ key, which contains a list of ordered object ids. When load_all method is called, the method yields objects in a prepared order::

  class Example(Model):
      id = Column()
      created_at = Column(types.DateTime, index_key=True)

  p.save(Example(created_at="2016-05-08 00:00:00"))
  p.save(Example(created_at="2016-05-08 01:00:00"))
  p.save(Example(created_at="2016-05-08 02:00:00"))
  p.save(Example(created_at="2016-05-08 05:00:00"))
  p.save(Example(created_at="2016-05-08 04:00:00"))
  assert [str(item.id) for item in p.load_all(Example)] == ["0", "1", "2", "4", "3"]
