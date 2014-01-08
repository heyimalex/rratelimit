-- ARGV[1] limit

local k = redis.call('GET', KEYS[1]) or 0
return tonumber(k) >= tonumber(ARGV[1])
