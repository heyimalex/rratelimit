--  ARGV[1] = current_bucket
local total = 0
for i=0,{buckets_div_2} do
    local bucket = (ARGV[1] - i)%{buckets}
    local ret = redis.call('HGET', KEYS[1], bucket)
    if ret then
        total = total + tonumber(ret)
        if total == {limit} then
            return true
        end
    end
end
return false
