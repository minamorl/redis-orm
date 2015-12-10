import operator
import redis
import inspect


DELETED = "__deleted__"
class PersistentData():

    def before_save(self):
        pass

    def before_load(self):
        pass

    def after_save(self, obj):
        pass

    def after_load(self):
        pass

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return str(self.id)


class Persistent():

    def __init__(self, prefix, key_separator=":", id_count="__latest__", r=None):
        self.prefix = prefix
        self.id_count = id_count
        self.key_separator = key_separator
        self.r = r or redis.StrictRedis(encoding='utf-8', decode_responses=True)

    def update_id(self, obj):
        classname = obj.__class__.__name__
        _id = self.get_last_insert_id(classname)
        if _id is not None:
            obj.id = _id + 1
            self.set_id(classname, obj.id)
        else:
            obj.id = 0
            self.set_id(classname, obj.id)
        return obj.id

    def get_last_insert_id(self, classname):
        _id = self.r.get(self.key_separator.join([self.prefix, classname, self.id_count]))
        return _id if _id is None else int(_id)

    def set_id(self, classname, id):
        return self.r.set(self.key_separator.join([self.prefix, classname, self.id_count]), str(id)) 

    def save(self, obj):
        r = self.r
        classname = obj.__class__.__name__
        params = inspect.signature(obj.__init__).parameters.values()
        obj.before_save()

        obj.id = obj.id or self.update_id(obj)
        obj.id = str(obj.id)

        for param in params:
            if getattr(obj, param.name) is not None:
                r.hset(self.key_separator.join([self.prefix, classname, obj.id]), param.name, getattr(obj, param.name))
            else:
                r.hdel(self.key_separator.join([self.prefix, classname, obj.id]), param.name)

        obj.after_save(obj)

    def load(self, cls, key):
        key = str(key)
        r = self.r
        classname = cls.__name__

        if r.hget(self.key_separator.join([self.prefix, classname, key]), DELETED):
            return None

        params = inspect.signature(cls.__init__).parameters.values()
        obj = cls(**{param.name: r.hget(self.key_separator.join([self.prefix, classname, key]), param.name) for param in params
            if hasattr(param, "name") and param.name != "self" and r.hget(self.key_separator.join([self.prefix, classname, key]), param.name) is not None})
        obj.after_load()
        return obj

    def load_all(self, cls, _range=None, reverse=False):
        max_id = self.get_max_id(cls)
        if max_id is None:
            return
        if _range is None:
            if reverse:
                _range = range(int(max_id), -1, -1)
            else:
                _range = range(int(max_id) + 1)
        for i in _range:
            yield self.load(cls, str(i))

    def load_all_only_keys(self, cls, key, reverse=False):
        max_id = self.get_max_id(cls)
        classname = cls.__name__
        if max_id is None:
            return
        _range = range(int(max_id) + 1)
        if reverse is True:
            _range = range(int(max_id), -1, -1)
        for i in _range:
            yield self.r.hget(self.key_separator.join([self.prefix, classname, str(i)]), key)

    def find(self, cls, cond):
        for item in self.load_all(cls):
            if cond(item) is True:
                return item
        return None

    def find_by(self, cls, key, value):
        max_id = self.get_max_id(cls)
        classname = cls.__name__
        if max_id is None:
            return
        for i in range(int(max_id) + 1):
            name = self.key_separator.join([self.prefix, classname, str(i)])
            if self.r.hget(name, key) == value:
                return self.load(cls, i)
        return None

    def get_max_id(self, cls):
        classname = cls.__name__
        if not self.r.exists(self.key_separator.join([self.prefix, classname, self.id_count])):
            return None
        return int(self.r.get(self.key_separator.join([self.prefix, classname, self.id_count])))

    def delete(self, obj):
        classname = obj.__class__.__name__
        if obj.id is None:
            return False
        return self.r.hset(self.key_separator.join([self.prefix, classname, obj.id]), DELETED, "1")

