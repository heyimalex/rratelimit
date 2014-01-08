import time

import redis
from nose.tools import raises

from rratelimit.exceptions import UnsupportedRedisVersion

class LimiterTestBase(object):

    def __init__(self, limiter_class, **kwargs):
        self.action = 'action'
        self.limit = 10
        self.period = 0.25

        r = redis.StrictRedis(host='localhost', port=6379)
        self.redis = r
        self.limiter = limiter_class(r, self.action, self.limit, self.period,
                                     **kwargs)

    def tearDown(self):
        self.limiter.clear('test')

    def test_get_key(self):
        assert self.limiter.get_key('test') == 'rratelimit:action:test'

    def test_clear(self):
        for r in range(self.limit*2):
            self.limiter.insert('test')
        self.limiter.clear('test')
        assert not self.limiter.check('test')

    def test_unlimited(self):
        "Test that check returns False when the limit is not exceeded"
        for r in range(self.limit-1):
            self.limiter.insert('test')
        assert not self.limiter.check('test')

    def test_limited(self):
        "Test that check returns True when the limit is exceeded"
        for r in range(self.limit):
            self.limiter.insert('test')
        assert self.limiter.check('test')

    def test_expires(self):
        "Test that insertions expire after `per` time has elapsed"
        for r in range(self.limit):
            self.limiter.insert('test')
        assert self.limiter.check('test')
        time.sleep(self.period)
        assert not self.limiter.check('test')

    def test_exact(self):
        for r in range(self.limit-1):
            self.limiter.insert('test')
        # kinda racy, should be fine as long as next 4
        # operations take less than 0.01s...
        assert not self.limiter.check('test')
        time.sleep(self.period-0.1)
        self.limiter.insert('test')
        assert self.limiter.check('test')
        time.sleep(0.1)
        assert not self.limiter.check('test')

    def test_pipeline(self):
        p = self.redis.pipeline()
        for r in range(self.limit):
            self.limiter.insert('test', p)
        self.limiter.check('test', p)
        assert p.execute()[-1]

    @raises(UnsupportedRedisVersion)
    def test_invalid_version(self):
        class Redismock(object):
            def info(self):
                return {'redis_version': '2.4.0'}
        mock = Redismock()
        self.limiter.check_ver(mock)

    def test_checked_insert(self):
        for r in range(self.limit):
            assert self.limiter.checked_insert('test')
        assert not self.limiter.checked_insert('test')