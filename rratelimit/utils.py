import math
import time
import os

class BaseLimiter(object):
    """Helper class, used to standardize key_prefix across Limiters"""
    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value
        self.key_prefix = 'rratelimit:{}:'.format(value)

    def check(self, *args, **kwargs):
        raise NotImplementedError

    def insert(self, *args, **kwargs):
        raise NotImplementedError

    def insert_if_under(self, *args, **kwargs):
        raise NotImplementedError

    def get_key(self, actor):
        return ''.join([self.key_prefix, actor])

basepath = os.path.abspath(os.path.dirname(__file__))
def load_templates(dirname):
    def load_file(*paths):
        path = os.path.join(basepath, dirname, *paths)
        return open(path).read()
    templates = {}
    templates['check'] = load_file('check.lua')
    templates['insert'] = load_file('insert.lua')
    templates['insert_if_under'] = load_file('insert_if_under.lua')
    return templates