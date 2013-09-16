import unittest

from utils import LimiterBase
from rratelimit import HashBasedLimiter
from rratelimit.hashbased import current_bucket

class CurrentBucketTest(unittest.TestCase):
    def run(self):
        self.assertEqual(current_bucket(0, 10, 1), 0)
        self.assertEqual(current_bucket(0.99, 10, 1), 0)
        self.assertEqual(current_bucket(1, 10, 1), 1)
        self.assertEqual(current_bucket(11, 10, 1), 1)
        self.assertEqual(current_bucket(1, 10, .5), 2)
        self.assertEqual(current_bucket(1.49, 10, .5), 2)

class HashBasedLimiterTest(LimiterBase):
    def setUp(self):
        self.limiter = HashBasedLimiter(self.redis_instance,
                                        action=self.action,
                                        limit=self.limit,
                                        period=self.period,
                                        accuracy=50*self.period)