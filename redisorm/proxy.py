import wrapt
import datetime


class BaseProxy(wrapt.ObjectProxy):

    def retrive(self):
        raise NotImplementedError()


class PersistentProxy(BaseProxy):

    def __init__(self, wrapped, cls=None, p=None):
        self.cls = cls
        self.p = p
        super().__init__(wrapped)

    def retrive(self, cls=self.cls, p=self.p):
        return p.find(cls, lambda x: x.id == str(self))

    def __str__(self):
        try:
            return str(self.__wrapped__.id)
        except AttributeError:
            return self.__wrapped__


class DatetimeProxy(BaseProxy):

    _format = "%Y-%m-%d %H:%M:%S"

    def retrive(self):
        return datetime.datetime.strptime(str(self), DatetimeProxy._format)

    def __str__(self):
        return str(self.__wrapped__.strftime(DatetimeProxy._format))


class IntProxy(BaseProxy):

    def retrive(self):
        try:
            return int(self)
        except TypeError:
            return 0


class BooleanProxy(BaseProxy):

    def retrive(self):
        return self == "True" or self

    def __init__(self, wrapped):
        wrapped = wrapped == "True" or wrapped is True
        super().__init__(wrapped)


class PersistentListProxy(BaseProxy):

    def __init__(self, wrapped, cls=None, p=None):
        self.cls = cls
        self.p = p
        super().__init__(wrapped)


    def _retrive(self, cls, p):
        for x in self:
            yield x.retrive(cls, p)

    def retrive(self, cls=self.cls, p=self.p):
        return list(self._retrive(cls, p))
