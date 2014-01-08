-- ARGV[1] limit
-- ARGV[2] period

local k = redis.call('GET', KEYS[1]) or 0
if tonumber(k) >= tonumber(ARGV[1]) then
    return false
end

redis.call('INCR', KEYS[1])
redis.call('PEXPIRE', KEYS[1], math.floor(ARGV[2]*1000))

return true
