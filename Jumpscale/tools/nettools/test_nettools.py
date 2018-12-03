import time

import pytest
from jumpscale import j


@pytest.mark.parametrize("addr,timeout, expected", [
    ("127.0.0.1", 10, True),
    ("8.8.8.8", 10, True),
    ("10.0.0.1", 10, False),
])
def test_pingMachine(addr, timeout, expected):
    assert j.sal.nettools.pingMachine(ip=addr, pingtimeout=timeout) == expected
