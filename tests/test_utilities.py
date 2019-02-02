from ddi.utilites import *


def test_hexlify_address():
    assert hexlify_address('127.0.0.1') == b'7f000001'


def test_unhexlify_address():
    assert unhexlify_address('7f000001') == '127.0.0.1'
