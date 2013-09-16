import time
import os

from ..utils import BaseLimiter, load_templates

templates = load_templates('simple')

class SimpleLimiter(BaseLimiter):

    def __init__(self, redis_instance, action, limit, period):
        self.action = action
        self.period = period
        
        pperiod = int(period*1000)

        check = templates['check'].format(limit=limit)
        insert = templates['insert'].format(period=pperiod)
        insert_if_under = templates['insert_if_under'].format(limit=limit,
                                                              period=pperiod)

        r = redis_instance # Just so I don't have to wrap lines...
        self._check = r.register_script(check)
        self._insert = r.register_script(insert)
        self._insert_if_under = r.register_script(insert_if_under)

    def check(self, actor, client=None):
        return bool(self._check(keys=[self.get_key(actor),],
                                client=client))

    def insert(self, actor, client=None):
        self._insert(keys=[self.get_key(actor),],
                     client=client)

    def insert_if_under(self, actor, client=None):
        return bool(self._insert_if_under(keys=[self.get_key(actor),],
                                          client=client))

    def get_key(self, actor):
        return ''.join([BaseLimiter.get_key(self, actor), ':',
                       str(int((time.time()/self.period)%3))])
