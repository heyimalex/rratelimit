local k = redis.call('GET', KEYS[1]) or 0
if tonumber(k) < {limit} then
    redis.call('INCR', KEYS[1])
    redis.call('PEXPIRE', KEYS[1], {period})
    return true
else
    return false
end