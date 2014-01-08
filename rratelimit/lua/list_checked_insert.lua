--  ARGV[1] = timestamp
--  ARGV[2] = period
--  ARGV[3] = limit

if redis.call('LLEN', KEYS[1]) < tonumber(ARGV[3]) then
    redis.call('LPUSH', KEYS[1], ARGV[1])
    redis.call('PEXPIRE', KEYS[1], math.floor(ARGV[2]*1000))
    return true
end

-- LTRIM before LINDEX so that LINDEX is O(1)
redis.call('LTRIM', KEYS[1], 0, ARGV[3] - 1)

local edge = redis.call('LINDEX', KEYS[1], ARGV[3] - 1)
local cutoff = ARGV[1] - ARGV[2]
if tonumber(edge) >= cutoff then
    return false
end

redis.call('LPUSH', KEYS[1], ARGV[1])
redis.call('PEXPIRE', KEYS[1], math.floor(ARGV[2]*1000))
return true