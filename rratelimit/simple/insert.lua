redis.call('INCR', KEYS[1])
redis.call('PEXPIRE', KEYS[1], {period})