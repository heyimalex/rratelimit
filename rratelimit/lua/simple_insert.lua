-- ARGV[1] period

redis.call('INCR', KEYS[1])
redis.call('PEXPIRE', KEYS[1], math.floor(ARGV[1]*1000))