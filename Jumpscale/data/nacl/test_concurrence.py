import sys
if '--gevent' in sys.argv:
    from gevent import monkey, pool
    monkey.patch_all()

import os
import pytest
from jumpscale import j


SECRET = '123456789012345678901234'
SIZE = 1024*500


def worker(name):
    nacl = j.data.nacl.get(sshkeyname='id_rsa')
    clear = os.urandom(SIZE)
    encrypted = nacl.encryptSymmetric(clear)
    decrypted = nacl.decryptSymmetric(encrypted)
    assert clear == decrypted


@pytest.mark.gevent
def test_concurrence():
    N = 2000
    p = pool.Pool()
    expected_secrets = ["greenlet_%d" % i for i in range(N)]
    p.map(worker, expected_secrets)
    p.join()
