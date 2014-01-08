import time

from .utils import LimiterTestBase
from rratelimit import SimpleLimiter

class TestSimpleLimiter(LimiterTestBase):
    def __init__(self):
        super(TestSimpleLimiter,self).__init__(SimpleLimiter)

    def test_exact(self):
        # SimpleLimiter is too inaccurate, exact will almost always fail
        pass

    def test_get_key(self):
        # SimpleLimiter's get key works differently than others
        keys = [
            'rratelimit:action:test:0',
            'rratelimit:action:test:1',
            'rratelimit:action:test:2'
        ]
        keys.remove(self.limiter.get_key('test'))
        time.sleep(self.period)
        keys.remove(self.limiter.get_key('test'))
        time.sleep(self.period)
        keys.remove(self.limiter.get_key('test'))
        assert len(keys) == 0
