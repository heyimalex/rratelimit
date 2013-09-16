local k = redis.call('GET', KEYS[1]) or 0
return tonumber(k) >= {limit}