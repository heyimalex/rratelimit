import time

from nose.tools import assert_raises

from .utils import LimiterTestBase
from rratelimit import ListLimiter

class TestListLimiter(LimiterTestBase):
    def __init__(self):
        super(TestListLimiter,self).__init__(ListLimiter)

    def test_check_ex(self):
        """Test check"""
        self.limiter.insert('test')
        self.limiter.insert('test')
        time.sleep(0.1)
        self.limiter.insert('test')
        self.limiter.insert('test')
        assert self.limiter.check_ex('test', 2, 0.05)
        assert not self.limiter.check_ex('test', 4, 0.05)
        assert self.limiter.check_ex('test', 4, 0.15)
        assert not self.limiter.check_ex('test', 5, 0.15)
        assert not self.limiter.check_ex('test', 5, 0.25)
        with assert_raises(ValueError):
            self.limiter.check_ex('test', self.limit + 1, 0.1)
        with assert_raises(ValueError):
            self.limiter.check_ex('test', 2, self.period + 0.1)
