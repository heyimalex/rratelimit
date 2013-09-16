import time
import os

from ..utils import BaseLimiter, load_templates

templates = load_templates('hashbased')

class HashBasedLimiter(BaseLimiter):
    def __init__(self, redis_instance, action, limit, period, accuracy):
        self.action = action
        self.total_buckets = accuracy*2
        self.bucket_size = float(period)/accuracy

        pperiod = int(1000*self.bucket_size*accuracy)
        data = {'buckets':self.total_buckets, 'buckets_div_2':accuracy,
                'limit':limit, 'period':period, 'pperiod':pperiod}

        check = templates['check'].format(**data)
        insert = templates['insert'].format(**data)
        insert_if_under = templates['insert_if_under'].format(**data)

        r = redis_instance # Just so I don't have to wrap lines...
        self._check = r.register_script(check)
        self._insert = r.register_script(insert)
        self._insert_if_under = r.register_script(insert_if_under)

    def insert(self, actor, client=None):
        self._insert(keys=[self.key_prefix+actor,],
                     args=[self.current_bucket(),],
                     client=client)

    def check(self, actor, client=None):
        return bool(self._check(keys=[self.key_prefix+actor,],
                                args=[self.current_bucket(),],
                                client=client))

    def insert_if_under(self, actor, client=None):
        return bool(self._insert_if_under(keys=[self.key_prefix+actor,],
                                          args=[self.current_bucket(),],
                                          client=client))

    def current_bucket(self):
        return current_bucket(time.time(), self.total_buckets,
                              self.bucket_size)

def current_bucket(current_time, total_buckets, bucket_size):
    return int((current_time/bucket_size)%total_buckets)