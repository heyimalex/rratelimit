import timeit
import random
import os

from redis import StrictRedis

redis = StrictRedis(host='localhost', port=6379) # Used to clean up test runs
basepath = os.path.abspath(os.path.dirname(__file__))

def make_setup(*args):
    imports = ""
    for a in args:
        imports += "{}, ".format(a)
    imports = imports[:-2] # Trim last comma+space
    setup = "import sys;sys.path.append('{}');".format(basepath)
    if imports != "":
        setup += "from testmethods import {};".format(imports)
    return setup

def cleanup(f):
    base_key = 'rratelimit:test:test'
    del_keys = [base_key,
                base_key + ':0',
                base_key + ':1',
                base_key +' :2']
    def wrapped(*args, **kwargs):
        redis.delete(*del_keys)
        out = f(*args, **kwargs)
        redis.delete(*del_keys)
        return out
    return wrapped

class Benchmark(object):
    def __init__(self, limit, period, accuracy, ratio=(1,1)):
        self.limit = limit
        self.period = period
        self.accuracy = accuracy
        self.ratio = ratio

    @cleanup
    def run_list_based(self, iterations):
        print "ListBasedLimiter:"
        setup = make_setup('redis', 'ListBasedLimiter', 'benchmark_limiter')
        setup += "lbl = ListBasedLimiter(redis, 'test', {}, {});"
        setup = setup.format(self.limit, self.period)
        stmt = 'benchmark_limiter(lbl, {}, {});'.format(self.ratio[0],
                                                        self.ratio[1])
        time = timeit.timeit(stmt, setup, number=iterations)
        print time
        return time

    @cleanup
    def run_hash_based(self, iterations):
        print "HashBasedLimiter:"
        setup = make_setup('redis', 'HashBasedLimiter', 'benchmark_limiter')
        setup += "hbl = HashBasedLimiter(redis, 'test', {}, {}, {});"
        setup = setup.format(self.limit, self.period, self.accuracy)
        stmt = 'benchmark_limiter(hbl, {}, {});'.format(self.ratio[0],
                                                        self.ratio[1])
        time = timeit.timeit(stmt, setup, number=iterations)
        print time
        return time

    @cleanup
    def run_simple(self, iterations):
        print "SimpleLimiter:"
        setup = make_setup('redis', 'SimpleLimiter', 'benchmark_limiter')
        setup += "sl = SimpleLimiter(redis, 'test', {}, {});"
        setup = setup.format(self.limit, self.period)
        stmt = 'benchmark_limiter(sl, {}, {});'.format(self.ratio[0],
                                                       self.ratio[1])
        time = timeit.timeit(stmt, setup, number=iterations)
        print time
        return time

    def run(self, iterations):
        self.run_list_based(iterations)
        self.run_hash_based(iterations)
        self.run_simple(iterations)
