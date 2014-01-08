--  ARGV[1] = timestamp
--  ARGV[2] = period

redis.call('LPUSH', KEYS[1], ARGV[1])
redis.call('PEXPIRE', KEYS[1], math.floor(ARGV[2]*1000))