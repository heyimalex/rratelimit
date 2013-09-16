import random

from redis import StrictRedis

from rratelimit import ListBasedLimiter
from rratelimit import HashBasedLimiter
from rratelimit import SimpleLimiter

redis = StrictRedis(host='localhost', port=6379)

def benchmark_limiter(limiter, insert, check):
    if weighted_random(insert, check):
        limiter.insert('test')
    else:
        limiter.check('test')

def weighted_random(a, b):
    return random.uniform(0, a+b) < a