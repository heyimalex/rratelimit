--  ARGV[1] = current_bucket
--  ARGV[2] = total buckets
--  ARGV[3] = limit

local total = 0
for i=0,math.floor(ARGV[2]/2) do
    local bucket = (ARGV[1] - i)%ARGV[2]
    local ret = redis.call('HGET', KEYS[1], bucket) or 0
    if ret then
        total = total + tonumber(ret)
        if total >= tonumber(ARGV[3]) then
            return true
        end
    end
end
return false
