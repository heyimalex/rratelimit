import os

from .exceptions import UnsupportedRedisVersion

basepath = os.path.abspath(os.path.dirname(__file__))


class AbstractLimiter(object):

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def get_key(self, actor):
        return ':'.join(['rratelimit', self.action, actor])

    def alert(self, *args, **kwargs):
        raise NotImplementedError

    def exceeded(self, *args, **kwargs):
        raise NotImplementedError

    def clear(self, *args, **kwargs):
        raise NotImplementedError


class LuaLimiter(AbstractLimiter):

    def __setattr__(self, name, value):
        if name == 'redis':
            self.check_ver(value)
            self.register_all(value)
        super(LuaLimiter, self).__setattr__(name, value)

    def register_script(self, redis, scriptname):
        """Register script located at ./lua/<scriptname>.lua"""
        path = os.path.join(basepath, 'lua', scriptname+'.lua')
        return redis.register_script(open(path).read())

    def register_all(self, *args, **kwargs):
        """Registers all lua scripts on redis instance'
           Must be overridden by child."""
        raise NotImplementedError

    def check_ver(self, redis):
        def versiontuple(v):
            return tuple(map(int, (v.split("."))))
        version = redis.info()['redis_version']
        if versiontuple(version) < versiontuple("2.6.0"):
            raise UnsupportedRedisVersion(version)


def dtime(timestamp, slots, period):
    """ Discrete time.

    Takes time and converts into into
    discrete cyclical blocks."""
    return int(timestamp / period) % slots
