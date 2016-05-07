class RedisType:
    __orderable__ = False

    def __init__(self, obj):
        if not isinstance(obj, type(self)):
            obj = self.parse(obj)
        self.obj = obj

    @classmethod
    def parse(self, string):
        return self.__class__(string)

    def freeze(self):
        return self.obj


class String(RedisType):
    pass


class Integer(RedisType):
    __orderable__ = True

    @classmethod
    def parse(self, string):
        return int(string)

    def freeze(self):
        return str(self.obj)


class DateTime(RedisType):
    __orderable__ = True

    @classmethod
    def parse(self, string):
        import dateutil.parser
        return self.__class__(dateutil.parser.parse(string))

    def freeze(self):
        self.obj.strftime("%Y-%m-%d %H:%M:%S")
