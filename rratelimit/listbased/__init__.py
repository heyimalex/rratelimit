import time
import math
import os

from ..utils import BaseLimiter, load_templates

templates = load_templates('listbased')

class ListBasedLimiter(BaseLimiter):

    def __init__(self, redis_instance, action, limit, period):
        self.action=action

        pperiod = int(math.ceil(period*1000))
        data = {'period':period, 'limit':limit, 'pperiod': pperiod}

        check = templates['check'].format(**data)
        insert = templates['insert'].format(**data)
        insert_if_under = templates['insert_if_under'].format(**data)
        
        r = redis_instance # Just so I don't have to wrap lines...
        self._check = r.register_script(check)
        self._insert = r.register_script(insert)
        self._insert_if_under = r.register_script(insert_if_under)

    def check(self, actor, client=None):
        return bool(self._check(keys=[self.key_prefix+actor,],
                                args=[time.time(),],
                                client=client))

    def insert(self, actor, client=None):
        self._insert(keys=[self.key_prefix+actor,],
                     args=[time.time(),],
                     client=client)

    def insert_if_under(self, actor, client=None):
        return bool(self._insert_if_under(keys=[self.key_prefix+actor,],
                                          args=[time.time(),],
                                          client=client))
