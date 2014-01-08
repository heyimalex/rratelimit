--  ARGV[1] = timestamp
--  ARGV[2] = period
--  ARGV[3] = limit

-- This could technically be excluded but I figured
-- that most calls to exceeded will be on keys that
-- don't even exist, so I optimize for that case.
if redis.call('LLEN', KEYS[1]) < tonumber(ARGV[3]) then
    return false
end

-- LTRIM before LINDEX so that LINDEX is O(1)
redis.call('LTRIM', KEYS[1], 0, ARGV[3] - 1)

local edge = redis.call('LINDEX', KEYS[1], ARGV[3] - 1)
local cutoff = ARGV[1] - ARGV[2]
return tonumber(edge) >= cutoff