local total = 0
for i=0,{buckets_div_2} do
    local bucket = (ARGV[1] - i)%{buckets}
    local ret = redis.call('HGET', KEYS[1], bucket)
    if ret then
        total = total + tonumber(ret)
        if total == {limit} then
            return false
        end
    end
end
redis.call('HINCRBY', KEYS[1], ARGV[1], 1)
redis.call('PEXPIRE', KEYS[1], {pperiod})

for i=0,{buckets_div_2} do
    local bucket = (ARGV[1] + i + 1)%{buckets}
    redis.call('HDEL', KEYS[1], bucket)
end
return true