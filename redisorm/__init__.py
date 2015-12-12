from . import core, proxy


def create_model(__name, **kwargs):

    import inspect
    import operator
    types = ", ".join(x[0] for x in sorted(kwargs.items(), key=operator.itemgetter(0)))
    _types = ", ".join(x[0] + "=None" for x in sorted(kwargs.items(), key=operator.itemgetter(0)))
    exec("def init(self, {_type}): self.__dict__.update(dict((str(x[0]), y) for x, y in zip(sorted(inspect.signature(init).parameters.items(), key=operator.itemgetter(0)) , ({type})) if str(x[0]) is not 'self'))".format(type=types, _type=_types), locals())

    class K(core.PersistentData):
        pass

    K.__init__ = locals()["init"]
    K.__name__ = __name

    return K


if __name__ == '__main__':
    main()
