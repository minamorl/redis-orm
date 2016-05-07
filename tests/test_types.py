from redisorm import types
import pytest


def test_type_datetime():
    types.DateTime('2011-11-03 18:21:26')


def test_type_string():
    types.String('This is a test.')


def test_type_int():
    types.Integer(123)
