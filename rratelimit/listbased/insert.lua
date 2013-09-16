--  ARGV[1] = (float) current timestamp
redis.call('LPUSH', KEYS[1], ARGV[1])
redis.call('PEXPIRE', KEYS[1], {pperiod})