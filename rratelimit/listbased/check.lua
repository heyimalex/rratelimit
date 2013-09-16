--  ARGV[1] = (float) current timestamp

local cutoff = ARGV[1] - {period}
local total = 0
local t = redis.call('LRANGE', KEYS[1], 0, {limit})
for i = 1, #t do
    if tonumber(t[i]) >= cutoff then
        total = total + 1
        if total == {limit} then
            redis.call('LTRIM', KEYS[1], 0, i - 1)
            return true
        end
    else
        redis.call('LTRIM', KEYS[1], 0, i - 2)
        break
    end
end
return false