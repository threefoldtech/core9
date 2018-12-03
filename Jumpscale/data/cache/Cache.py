
from Jumpscale import j
import pickle
import time

JSBASE = j.application.jsbase_get_class()


class Cache(JSBASE):

    def __init__(self):
        self._location = "j.data.cache"
        JSBASE.__init__(self)
        self._cache = {}

    def serialize(self, val):
        tt = j.data.types.type_detect(val)

    def get(self, id="main", reset=False, expiration=30):
        """
        @param id is a unique id for the cache
        db = when none then will be in memory
        """
        if not id in self._cache:
            self._cache[id] = CacheCategory(id=id, expiration=expiration, reset=reset)
        return self._cache[id]

    def resetAll(self):
        for key, cache in self._cache.items():
            cache.reset()

    def reset(self, id=None):
        if id is None:
            self.resetAll()
        else:
            if id in self._cache:
                self._cache[id].reset()

    def test(self):
        """
        js_shell 'j.data.cache.test()'
        """
        def testAll(c):
            c.set("something", "OK")
            assert "something" in c.list()
            assert c.exists("something") is True
            c.reset()
            assert c.exists("something") is False
            c.set("something", "OK")
            self.logger.debug("RESET ALL")
            self.reset()
            assert c.exists("something") is False

            c.set("something", "OK")
            assert "OK" == c.get("something")

            def return1():
                return 1

            def return2():
                return 2

            def return3():
                return 3

            assert c.get("somethingElse", return1) == 1
            assert c.get("somethingElse") == 1

            c.reset()

            try:
                c.get("somethingElse")
            except Exception as e:
                if not "Cannot get 'somethingElse' from cache" in str(e):
                    raise RuntimeError("error in test. non expected output")

            self.logger.debug("expiration test")
            time.sleep(2)

            assert c.get("somethingElse", return2, expire=1) == 2
            # still needs to be 2
            assert c.get("somethingElse", return3, expire=1) == 2
            time.sleep(2)
            assert c.get("somethingElse", return3,
                         expire=1) == 3  # now needs to be 3

            assert c.get("somethingElse", return2, expire=100, refresh=True) == 2
            assert c.exists("somethingElse")
            time.sleep(2)
            assert c.exists("somethingElse")
            assert "somethingElse" in c.list()
            self.reset()
            assert c.exists("somethingElse") is False
            assert "somethingElse" not in c.list()

        self.logger.debug("REDIS CACHE TEST")
        # make sure its redis
        j.clients.redis.core_get()
        j.core.db_reset()
        c = self.get("test", expiration=1)
        testAll(c)

        # now stop redis
        j.clients.redis.kill()
        j.core.db_reset()
        self.logger.debug("MEM CACHE TEST")
        c = self.get("test", expiration=1)
        testAll(c)
        self.logger.debug("TESTOK")


class CacheCategory(JSBASE):

    def __init__(self, id, expiration=10, reset=False):
        JSBASE.__init__(self)
        self.id = id
        self.db = j.core.db
        self.hkey = "cache:%s" % self.id
        self.expiration = expiration
        if reset:
            self.reset()

    def _key_get(self, key):
        return "cache:%s:%s" % (self.id, key)

    def delete(self, key):
        self.db.delete(self._key_get(key))

    def set(self, key, value, expire=None):
        if expire is None:
            expire = self.expiration
        self.db.set(self._key_get(key), pickle.dumps(value), ex=expire)

    def exists(self, key):
        return self.db.get(self._key_get(key)) != None

    def get(self, key, method=None, expire=None, refresh=False, **kwargs):
        """

        """
        # check if key exists then return (only when no refresh)
        res = self.db.get(self._key_get(key))
        if res != None:
            res = pickle.loads(res)
        if expire is None:
            expire = self.expiration
        # print("res:%s"%res)
        if refresh or res is None:
            if method is None:
                raise j.exceptions.RuntimeError(
                    "Cannot get '%s' from cache,not found & method None" % key)
            # print("cache miss")
            val = method(**kwargs)
            # print(val)
            if val is None or val == "":
                raise j.exceptions.RuntimeError(
                    "cache method cannot return None or empty string.")
            self.set(key, val, expire=expire)
            return val
        else:
            if res is None:
                raise j.exceptions.RuntimeError(
                    "Cannot get '%s' from cache" % key)
            return res

    def reset(self):
        self.logger.debug("RESET")
        for item in self.list():
            self.logger.debug("DELETE:%s" % item)
            self.delete(item)

    def list(self):
        return [item.decode().split(":")[-1] for item in self.db.keys("cache:%s:*" % self.id)]

    def __str__(self):
        res = {}
        for key in self.db.keys():
            val = self.db.get(key)
            res[key] = val
        # out = j.data.serializer.yaml.dumps(res, default_flow_style=False)
        out = j.data.serializer.yaml.dumps(res)
        return out

    __repr__ = __str__
