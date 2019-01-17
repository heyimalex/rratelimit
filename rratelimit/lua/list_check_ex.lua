--  ARGV[1] = timestamp
--  ARGV[2] = period
--  ARGV[3] = limit

-- Assuming values(=timestamps) in list are sorted (high-to-low), this script
-- checks whether `limit` items exists within `period` or not
-- (where value >= timestamp-period)

if redis.call('LLEN', KEYS[1]) < tonumber(ARGV[3]) then
    return false
end

-- LIST may contain more items than `limit` and should not be trimmed
local edge = redis.call('LINDEX', KEYS[1], ARGV[3] - 1)
local cutoff = ARGV[1] - ARGV[2]
return tonumber(edge) >= cutoff
