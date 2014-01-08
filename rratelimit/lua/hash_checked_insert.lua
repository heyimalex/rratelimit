--  ARGV[1] = current_bucket
--  ARGV[2] = total buckets
--  ARGV[3] = limit
--  ARGV[4] = period

local total = 0
for i=0,math.floor(ARGV[2]/2) do
    local bucket = (ARGV[1] - i)%ARGV[2]
    local ret = redis.call('HGET', KEYS[1], bucket) or 0
    if ret then
        total = total + tonumber(ret)
        if total >= tonumber(ARGV[3]) then
            return false
        end
    end
end

redis.call('HINCRBY', KEYS[1], ARGV[1], 1)
redis.call('PEXPIRE', KEYS[1], math.floor(ARGV[4]*1000))

for i=0,math.floor(ARGV[2]/2) do
    local bucket = (ARGV[1] + i + 1)%ARGV[2]
    redis.call('HDEL', KEYS[1], bucket)
end

return true
