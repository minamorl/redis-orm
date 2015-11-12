import operator
import redis
import inspect


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
        if self.r.get(self.key_separator.join([self.prefix, classname, self.id_count])) is not None:
            obj.id = int(self.r.get(self.key_separator.join([self.prefix, classname, self.id_count]))) + 1
            self.r.set(self.key_separator.join([self.prefix, classname, self.id_count]), obj.id)
        else:
            obj.id = 0
            self.r.set(self.key_separator.join([self.prefix, classname, self.id_count]), "0")
        return obj.id

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
        params = inspect.signature(cls.__init__).parameters.values()
        obj = cls(**{param.name: r.hget(self.key_separator.join([self.prefix, classname, key]), param.name) for param in params
            if hasattr(param, "name") and param.name != "self" and r.hget(self.key_separator.join([self.prefix, classname, key]), param.name) is not None})
        obj.after_load()
        return obj

    def load_all(self, cls):
        classname = cls.__name__
        if not self.r.exists(self.key_separator.join([self.prefix, classname, self.id_count])):
            return
        max_id = self.r.get(self.key_separator.join([self.prefix, classname, self.id_count]))
        for i in range(int(max_id) + 1):
            yield self.load(cls, str(i))

    def find(self, cls, cond):
        for item in self.load_all(cls):
            if cond(item) is True:
                return item
        return None
