class RedisType:
    __orderable__ = False

    def __init__(self, obj):
        if not isinstance(obj, type(self)) and obj is not None:
            obj = self.parse(obj)
        self.obj = obj

    @classmethod
    def parse(cls, string):
        return string

    def freeze(self):
        return self.obj

    def __str__(self):
        return self.freeze()



class String(RedisType):
    pass


class Integer(RedisType):
    __orderable__ = True

    @classmethod
    def parse(cls, string):
        return int(string)

    def freeze(self):
        return str(self.obj)


class DateTime(RedisType):
    __orderable__ = True

    @classmethod
    def parse(cls, string):
        import dateutil.parser
        import datetime
        if isinstance(string, datetime.datetime):
            return string
        return dateutil.parser.parse(string)
        

    def freeze(self):
        return self.obj.strftime("%Y-%m-%d %H:%M:%S")

class Boolean(RedisType):

    @classmethod
    def parse(cls, string):
        if isinstance(string, bool):
            return string
        return "True" == string

    def freeze(self):
        return str(self.obj)
