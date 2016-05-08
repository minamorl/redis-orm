from redisorm import types
import pytest


def test_type_datetime():
    dt = types.DateTime('2011-11-03 18:21:26')
    assert '2011-11-03 18:21:26' == dt.freeze()


def test_type_string():
    assert types.String('This is a test.').freeze() == "This is a test."


def test_type_int():
    assert types.Integer(123).freeze() == "123"
    assert types.Integer("123").freeze() == "123"


def test_type_boolean():
    assert types.Boolean(True).freeze() == "True"
    assert types.Boolean("False").freeze() == "False"
    assert types.Boolean(False).freeze() == "False"
