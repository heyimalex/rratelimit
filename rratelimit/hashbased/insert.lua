--  ARGV[1] = current_bucket

redis.call('HINCRBY', KEYS[1], ARGV[1], 1)
redis.call('PEXPIRE', KEYS[1], {pperiod})

for i=0,{buckets_div_2} do
    local bucket = (ARGV[1] + i + 1)%{buckets}
    redis.call('HDEL', KEYS[1], bucket)
end