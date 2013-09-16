from utils import LimiterBase
from rratelimit import ListBasedLimiter

class ListBasedLimiterTest(LimiterBase):
    def setUp(self):
        self.limiter = ListBasedLimiter(self.redis_instance,
                                        action=self.action,
                                        limit=self.limit,
                                        period=self.period)
