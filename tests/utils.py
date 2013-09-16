import unittest
import time

import redis

class LimiterBase(unittest.TestCase):

    def __init__( self, *args, **kwargs ):
        super(LimiterBase, self).__init__(*args, **kwargs)

        self.action = 'test_action'
        self.limit = 10
        self.period = 0.25
        self.redis_instance = redis.StrictRedis(host='localhost', port=6379)

        if self.__class__ != LimiterBase:
            self.run = unittest.TestCase.run.__get__(self, self.__class__)
        else:
          self.run = lambda self, *args, **kwargs: None

    def tearDown(self):
        self.redis_instance.delete('rratelimit:{}:test'.format(self.action))
        self.redis_instance.delete('rratelimit:{}:test:0'.format(self.action))
        self.redis_instance.delete('rratelimit:{}:test:1'.format(self.action))
        self.redis_instance.delete('rratelimit:{}:test:2'.format(self.action))
    
    def test_unlimited(self):
        """Test that check returns False when the limit is not exceeded"""
        for r in range(self.limit-1):
            self.limiter.insert('test')
        self.assertFalse(self.limiter.check('test'))

    def test_limited(self):
        """Test that check returns True when the limit is exceeded"""
        for r in range(self.limit):
            self.limiter.insert('test')
        self.assertTrue(self.limiter.check('test'))

    def test_expires(self):
        """Test that insertions expire after per time has elapsed"""
        for r in range(self.limit):
            self.limiter.insert('test')
        self.assertTrue(self.limiter.check('test'))
        time.sleep(self.period)
        self.assertFalse(self.limiter.check('test'))

    def test_exact(self):
        for r in range(self.limit-1):
            self.limiter.insert('test')
        # kinda racy, should be fine as long as next 4
        # opperations take less than 0.1s...
        self.assertFalse(self.limiter.check('test'))
        time.sleep(self.period-0.1)
        self.limiter.insert('test')
        self.assertTrue(self.limiter.check('test'))
        time.sleep(0.1)
        self.assertFalse(self.limiter.check('test'))

    def test_insert_if_under(self):
        for r in range(self.limit):
            self.assertTrue(self.limiter.insert_if_under('test'))
        self.assertFalse(self.limiter.insert_if_under('test'))