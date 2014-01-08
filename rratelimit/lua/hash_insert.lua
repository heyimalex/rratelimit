--  ARGV[1] = current_bucket
--  ARGV[2] = total buckets
--  ARGV[3] = period

redis.call('HINCRBY', KEYS[1], ARGV[1], 1)
redis.call('PEXPIRE', KEYS[1], math.floor(ARGV[3]*1000))

for i=0,math.floor(ARGV[2]/2) do
    local bucket = (ARGV[1] + i + 1)%ARGV[2]
    redis.call('HDEL', KEYS[1], bucket)
end