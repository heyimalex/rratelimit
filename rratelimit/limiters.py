import time

from .utils import LuaLimiter, dtime


class ListLimiter(LuaLimiter):

    def __init__(self, redis, action, limit, period):
        self.redis = redis
        self.action = action
        self.limit = limit
        self.period = period

    def register_all(self, redis):
        self._insert = self.register_script(redis, 'list_insert')
        self._check = self.register_script(redis, 'list_check')
        self._check_ex = self.register_script(redis, 'list_check_ex')
        self._checked_insert = self.register_script(redis,
                                                    'list_checked_insert')

    def clear(self, actor):
        self.redis.delete(self.get_key(actor))

    def insert(self, actor, client=None):
        self._insert(
            keys=[self.get_key(actor), ],
            args=[time.time(), self.period],
            client=client
        )

    def check(self, actor, client=None):
        return bool(self._check(
            keys=[self.get_key(actor), ],
            args=[time.time(), self.period, self.limit],
            client=client
        ))

    def check_ex(self, actor, limit, period, client=None):
        if period > self.period or limit > self.limit:
            raise ValueError('Cannot check with higher limit or period')
        return bool(self._check_ex(
            keys=[self.get_key(actor), ],
            args=[time.time(), period, limit],
            client=client
        ))

    def checked_insert(self, actor, client=None):
        return bool(self._checked_insert(
            keys=[self.get_key(actor), ],
            args=[time.time(), self.period, self.limit],
            client=client,
        ))


class HashLimiter(LuaLimiter):

    def __init__(self, redis, action, limit, period, accuracy):
        self.redis = redis
        self.action = action
        self.limit = limit
        self.period = period
        self.accuracy = accuracy
        self.total_buckets = accuracy*2
        self.bucket_size = period/float(accuracy)

    def register_all(self, redis):
        self._insert = self.register_script(redis, 'hash_insert')
        self._check = self.register_script(redis, 'hash_check')
        self._checked_insert = self.register_script(redis,
                                                    'hash_checked_insert')

    def clear(self, actor):
        self.redis.delete(self.get_key(actor))

    def current_bucket(self):
        return dtime(time.time(), self.total_buckets, self.bucket_size)

    def insert(self, actor, client=None):
        self._insert(
            keys=[self.get_key(actor), ],
            args=[
                self.current_bucket(),
                self.total_buckets,
                self.period],
            client=client
        )

    def check(self, actor, client=None):
        return bool(self._check(
            keys=[self.get_key(actor), ],
            args=[self.current_bucket(), self.total_buckets, self.limit],
            client=client
        ))

    def checked_insert(self, actor, client=None):
        return bool(self._checked_insert(
            keys=[self.get_key(actor), ],
            args=[
                self.current_bucket(),
                self.total_buckets,
                self.limit,
                self.period],
            client=client
        ))


class SimpleLimiter(LuaLimiter):

    def __init__(self, redis, action, limit, period):
        self.redis = redis
        self.action = action
        self.limit = limit
        self.period = period

    def get_key(self, actor):
        orig = super(SimpleLimiter, self).get_key(actor)
        current = dtime(time.time(), 3, self.period)
        return "{}:{}".format(orig, current)

    def clear(self, actor):
        orig = super(SimpleLimiter, self).get_key(actor)
        self.redis.delete(orig + ":0")
        self.redis.delete(orig + ":1")
        self.redis.delete(orig + ":2")

    def register_all(self, redis):
        self._insert = self.register_script(redis, 'simple_insert')
        self._check = self.register_script(redis, 'simple_check')
        self._checked_insert = self.register_script(redis,
                                                    'simple_checked_insert')

    def insert(self, actor, client=None):
        self._insert(
            keys=[self.get_key(actor), ],
            args=[self.period, ],
            client=client
        )

    def check(self, actor, client=None):
        return bool(self._check(
            keys=[self.get_key(actor), ],
            args=[self.limit, ],
            client=client
        ))

    def checked_insert(self, actor, client=None):
        return bool(self._checked_insert(
            keys=[self.get_key(actor), ],
            args=[self.limit, self.period],
            client=client
        ))
