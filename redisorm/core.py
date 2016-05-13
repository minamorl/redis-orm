import redis
from . import types

DELETED = "__deleted__"
SORTED = "__sorted__"


class RedisOrmException(Exception):
    pass


class MetaModel(type):
    def __new__(mcs, name, bases, attrs):
        # Create temporary class
        cls = super().__new__(mcs, name, bases, attrs)
        attrs["_columns"] = []
        attrs["_index_key"] = None
        for attr in attrs:
            if attr.startswith("_"):
                continue
            if isinstance(cls.__dict__[attr], Column):
                if cls.__dict__[attr].index_key:
                    if attrs["_index_key"]:
                        raise RedisOrmException(
                            "Model should have only one index key.")
                    attrs["_index_key"] = attr

                attrs["_columns"].append(attr)
        return super().__new__(mcs, name, bases, attrs)


class Column():
    def __init__(self, type=None, default=None, index_key=False):
        self.type = type
        self.default = default
        self.index_key = False
        if index_key:
            if self.type.__orderable__:
                self.index_key = index_key
            else:
                raise RedisOrmException()


class Model(metaclass=MetaModel):
    def set_column(self, column, obj):
        if self.__class__.__dict__[column].type is None or isinstance(
                obj, self.__class__.__dict__[column].type):
            self.__dict__[column] = obj
        else:
            self.__dict__[column] = self.__class__.__dict__[column].type(obj)

    def __init__(self, *args, **kwargs):
        for column in self._columns:
            import types
            if isinstance(self.__class__.__dict__[column].default,
                          types.FunctionType):
                self.set_column(column, kwargs.get(
                    column, self.__class__.__dict__[column].default()))
            else:
                self.set_column(column, kwargs.get(
                    column, self.__class__.__dict__[column].default))

    def __getattribute__(self, attr):
        obj = object.__getattribute__(self, attr)
        if isinstance(obj, types.RedisType):
            return obj.obj
        return obj

    def __setattr__(self, name, value):
        self.set_column(name, value)


class Client():
    def __init__(self,
                 prefix,
                 key_separator=":",
                 id_count="__latest__",
                 r=None):
        self.prefix = prefix
        self.id_count = id_count
        self.key_separator = key_separator
        self.r = r or redis.StrictRedis(encoding='utf-8',
                                        decode_responses=True)

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
        _id = self.r.get(self.key_separator.join([self.prefix, classname,
                                                  self.id_count]))
        return _id if _id is None else int(_id)

    def set_id(self, classname, id):
        return self.r.set(
            self.key_separator.join([self.prefix, classname, self.id_count]),
            str(id))

    def save(self, obj):
        r = self.r
        classname = obj.__class__.__name__

        obj.id = obj.id or self.update_id(obj)
        obj.id = str(obj.id)

        for param in obj._columns:
            if obj.__dict__[param] is not None:
                if obj.__class__.__dict__[param].type:
                    key = self.key_separator.join([self.prefix, classname, str(
                        obj.id)])
                    r.hset(key, param,
                           getattr(obj.__class__,
                                   param).type(getattr(obj, param)).freeze())
                else:
                    r.hset(
                        self.key_separator.join([self.prefix, classname, obj.id
                                                 ]), param, getattr(obj,
                                                                    param))
            else:
                r.hdel(
                    self.key_separator.join([self.prefix, classname, obj.id]),
                    param)

        if obj.__class__._index_key:
            r.delete(self.key_separator.join([self.prefix, classname, SORTED]))
            for item in self.load_all(obj.__class__):
                r.rpush(
                    self.key_separator.join([self.prefix, classname, SORTED]),
                    item.id)

    def load(self, cls, key):
        key = str(key)
        r = self.r
        classname = cls.__name__

        if r.hget(
                self.key_separator.join([self.prefix, classname, key]),
                DELETED):
            return None

        def _load(columns):
            for column in columns:
                val = r.hget(
                    self.key_separator.join([self.prefix, classname, key]),
                    column)
                if column != "self" and val is not None:
                    if cls.__dict__[column].type is None:
                        yield column, val
                    else:
                        yield column, cls.__dict__[column].type(val)

        obj = cls(**dict(_load(cls._columns)))
        return obj

    def load_all(self,
                 cls,
                 _range=None,
                 reverse=False,
                 ignore_index_key=False):
        max_id = self.get_max_id(cls)
        if max_id is None:
            return
        if _range is None:
            if reverse:
                _range = range(int(max_id), -1, -1)
            else:
                _range = range(int(max_id) + 1)
        if cls._index_key and not ignore_index_key:
            k = self.load_all_only_keys(cls, "id", ignore_index_key=True)
            v = self.load_all_only_keys(
                cls, cls._index_key, ignore_index_key=True)
            kv = zip(k, v)
            if kv is None:
                return
            for i, _ in sorted(kv, key=lambda tp: tp[1]):
                yield self.load(cls, str(i))
        else:
            for i in _range:
                yield self.load(cls, str(i))

    def load_all_only_keys(
            self, cls, key,
            reverse=False,
            ignore_index_key=False):
        if ignore_index_key or cls._index_key is None:
            max_id = self.get_max_id(cls)
            classname = cls.__name__
            if max_id is None:
                return
            _range = range(int(max_id) + 1)
            if reverse is True:
                _range = range(int(max_id), -1, -1)
            for i in _range:
                yield self.r.hget(
                    self.key_separator.join([self.prefix, classname, str(i)]),
                    key)
        else:
            k = self.load_all_only_keys(
                cls, cls._index_key, ignore_index_key=True)
            v = self.load_all_only_keys(cls, key, ignore_index_key=True)
            kv = zip(k, v)
            for _, val in sorted(kv, key=lambda tp: tp[0]):
                yield val

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
        if not self.r.exists(self.key_separator.join([self.prefix, classname,
                                                      self.id_count])):
            return None
        return int(self.r.get(self.key_separator.join([self.prefix, classname,
                                                       self.id_count])))

    def delete(self, obj):
        classname = obj.__class__.__name__
        if obj.id is None:
            return False
        return self.r.hset(
            self.key_separator.join([self.prefix, classname, obj.id]), DELETED,
            "1")

# backword compatible
Persistent = Client
MetaPersistentData = MetaModel
PersistentData = Model


def create_model(__name, **kwargs):
    attrs = {}

    for key, val in kwargs.items():
        if not isinstance(val, Column):
            raise RedisOrmException(
                "create_model args can only accepts instance of Column.")
        attrs[key] = val

    cls = type(__name, (Model, ), attrs)
    return cls
