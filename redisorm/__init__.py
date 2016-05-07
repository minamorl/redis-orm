from . import core, types
from .core import Persistent, PersistentData, Column


def create_model(__name, **kwargs):
    attrs = {}

    for key, val in kwargs.items():
        attrs[key] = core.Column(val)

    cls = type(__name, (core.PersistentData, ), attrs)
    return cls

if __name__ == '__main__':
    main()
