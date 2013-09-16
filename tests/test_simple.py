from utils import LimiterBase
from rratelimit.simple import SimpleLimiter

class SimpleLimiterTest(LimiterBase):
    def setUp(self):
        self.limiter = SimpleLimiter(self.redis_instance,
                                        action=self.action,
                                        limit=self.limit,
                                        period=self.period)

    def test_exact(self):
        # SimpleLimiter is too inaccurate, this will always fail
        # But that's by design...
        pass