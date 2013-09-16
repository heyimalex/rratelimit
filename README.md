# rratelimit

Rate limiting classes for use with redis and redis-py.

### Installation

Install via pip

    pip install rratelimit

Install from source

    git clone git://github.com/HeyImAlex/rratelimit.git
    cd rratelimit
    python setup.py

requires redis-server >= 2.6.0 to work properly

### Usage

In plain english, the rate limiters allow you to

    Limit {actor} from doing {action} {limit} times per {period} seconds

Each rate limiter shares the same basic interface:

* constructor params
    * **redis_instance**: redis-py Redis or StrictRedis object
    * **action**: String name for the action this limiter will limit
    * **limit**:  Inclusive number of times you'd like `action` to be able to be executed per `period` seconds
    * **period**: Time window in which you want to limit `action`
* methods
    * **check**(`actor`): Return whether `actor` is over the limit for this action.
    * **insert**(`actor`): Let the limiter know that `actor` has just completed this action.
    * **insert_if_under**(`actor`): Convenience method for atomically checking if an actor is over the limit and, if they're not, running the insert method. Returns True if the insert suceeded, False if the user was over the limit.

Each method is atomic and thread safe. Internally rratelimit uses redis' EVALSHA command, so it's fairly fast too.

### Example

Say you're writing forum software in Flask and you want to limit your users to only be able to create a thread once every five minutes. Outside of any request context, create an instance of Limiter with the proper parameters. In this case the `action` would be something like `"new_thread"`, the `limit` would be `1`, and the `period` would be `5*60`.

```python

from redis import StrictRedis
from rratelimit import Limiter

r = StrictRedis(...)
new_thread_limiter = Limiter(r, action='new_thread', limit=1, period=5*60)

```

Now in your view function all you need to do is call 'insert_if_under' whenever a user attempts to create a new thread. If it returns True, you know that the user was not over the limit and you can proceed to create the thread.

```python

@app.route('/new_thread', methods=['GET', 'POST'])
def new_thread():
    form = NewThreadForm(request.form)
    if request.method == 'POST' and form.validate():
        # Do some stuff
        if new_thread_limiter.insert_if_under(request.remote_addr):
            # Create the thread
        else:
            # You were over the limit!

```

Hot like pizza supper.

## Classes

Internally rratelimit has a couple of different Limiter classes. The default (and the one that's returned when you call Limiter) is the ListBasedLimiter, and for most cases it'll do just fine. However, if you're handling anything that's performance intensive **or** you're running into performance issues, you'll probably want to get acquainted with all of the different types.

### ListBasedLimiter
* **pros** - simple, accurate, O(1) insert time
* **cons** - O(N) check time, memory usage, where N is the number of insertions made, not great for large `limit` and `period` values.

The ListBasedLimiter works by LPUSHing a timestamp onto a list every time insert is called. It checks the limit by calling `LRANGE 0, {limit}` and iterating through the returned table until it either reaches the end of the table, reaches `limit` total iterations, or reaches a value below a cut off point defined as `current_timestamp - period`. If the total number of timestamps it finds is greater than or equal to `limit`, check returns true. Check also LTRIMs all items past the item that it completes on, ensuring that after a check the list is at most `limit` keys long. Expiration is handled by setting a ttl equal to `period` on insert.

If you solely use insert_if_under on a ListBasedLimiter you're guaranteed to do no more than `2*limit` operations per run, which makes it constant time. If you use check and insert separately, the bound is O(N) but the average case will be constant time. The thing to remember is that insert time, check time, and memory usage scales with `limit`.

**Note**: There is an edge case where ListBasedLimiters can use a large amount of memory; if you continually insert before the key expires without ever calling check, the list will never be trimmed. This trade off is made to maintain O(1) insert time.

### HashBasedLimiter
* **pros** - O(1) inserts, checks, and memory usage
* **cons** - more complicated, inherently inaccurate, constant big-O benefits sometimes negated by size of constant if you still need great accuracy on a long period.

The HashBasedLimiter is more complicated. It takes an additional constructor param, `accuracy`, which basically defines a speed/accuracy tradeoff;

* acceptable error = period/accuracy seconds
* O(1) insert/check/memory where the constant is equal to accuracy

The HashBasedLimiter internally works by creating `2*accuracy` "time buckets" arranged in a circle. Each time bucket represents `period/accuracy` seconds, and the current bucket is found by taking the current timestamp, dividing it by the bucket width, and then computing the modulo with the total number of buckets. When insert is called, the limiter finds the current bucket and INCRs it, clears half of the buckets in front of it (up to where the period starts), and sets an expire time equal to `period`. When check is called, the limiter just adds up the contents of the bucket and half of the total buckets behind it. Whew.

The main takeaway here is that memory footprint, check times and insert times all scale with the accuracy parameter. If you don't need great accuracy and your `limit` is high, the HashBasedLimiter may be better suited for your usecase. If you *really* don't need great accuracy, the SimpleLimiter might be a good match.

### SimpleLimiter
* **pros** - very low memory footprint (at most 2 keys per actor), very fast, very simple, good enough for many situations
* **cons** - inaccurate, allows up to 2x `limit` to be executed in short period of time.

The SimpleLimiter is... very simple. Basically it just INCRs a key on insert and then checks if the contents of the current key is greater than or equal to `limit`. The current key is found by dividing the current timestamp by `period` and taking the modulo of that with 3. Expiration is set on insert to `period`.

The important thing to know is that this isn't a "moving window" limiter; it doesn't make the guarantee that an actor can't make more than `limit` calls in the last `period` seconds, just that an actor can't make more than `limit` calls in period `x`.

## Race conditions

Sometimes you may want to chain multiple inserts or checks in an atomic way. Using locks is usually cumbersome and comes with overhead, so rratelimit provides an alternative through redis-py's pipelines.

Just create a pipeline and then call the limiter method you want with the pipeline object as the second parameter.

```python
r = redis.Redis(...)
my_limiter = Limiter(...)
# Create a pipeline
pipe = r.pipeline()
# Do some stuff
pipe.set('foo', 'bar')
# Add in your limiter call
my_limiter.check('some_actor', pipe)
# Do some other stuff
pipe.get('foo')
# Execute the pipe
pipe.execute()
# [True, False, 'bar']
# (second item is the return from check)

```

## Benchmarking

In the repo I've provided a really simple benchmarking package to use. It's not particularly robust or well tested, but it might be a good place to start. Using it looks like this:

```python
from benchmark import Benchmark

b = Benchmark(limit=1, period=30, accuracy=30, ratio=(2, 1))
b.run(1000)
# ListBasedLimiter:
# 0.581626176834
# HashBasedLimiter:
# 1.29797101021
# SimpleLimiter:
# 0.549144029617

```
This will run the benchmark for 1000 iterations on each of the limiters with the provided args and print out the results. The `ratio` param is a tuple that represents the ratio of inserts:checks to perform. This currently requires redis-py (`pip install redis`) to use.

### TODO

* Improve docs
* Improve tests

## Misc

* Running check and insert separately to see if an actor can do an action creates a race condition; if another check is initiated before the insert is run, both checks could return False. Use insert_if_under to protect against this.
* Technically rratelimit has no dependencies outside the standard library; while limiters take a redis-py object, it never actually constructs one.
* Because redis is single threaded, every limiter method blocks while it's executing. HashBasedLimiters that take a long time to execute make all types of weird stuff happen. List based limiters still work fairly well.
* The limiter classes are all essentially immutable after construction.
* The limiters use EVALSHA and Lua scripts internally for most of the logic.
* Current time is provided by python, not Lua. This is better for a couple of reasons, but redis doesn't provide the os library so doing it through Lua isn't possible anyways.
* The Lua scripts are small, but I suppose if you're creating a ton of distinct limiters there's a possibility that redis' script cache could fill up. Flushing the script cache might be good from time to time?
* redis >= 2.6.0 is required because rratelimit uses PEXPIRE.
* Don't do stupid stuff because rratelimit won't catch it and you'll probably just get an incomprehensible error from the Lua interpreter.
* Actions and actors should probably only contain letters, numbers, periods, dashes and underscores. I can't think of a situation where something bad would happen with strange keys, but I'd maybe play it safe. I'll look into this...
* Keys are generally of the form `rratelimit:{action}:{actor}'. It goes without saying that you probably shouldn't make keys that start with 'rratelimit' in other places in your application. I'm considering adding a random string to the limiter instance at construction that gets added in there, but I like that multiple instances with the same params can act with the same data.
* Subsecond/noninteger periods are technically allowed, but you're sort of at the mercy of the system for them to work properly. The test suite is run with a period of .5s and it works fine.
* Package layout is a little unorthodox/doesn't follow best practices, but it's convenient to have the Lua scripts in the same dir as their respective limiter, and enforcing strict adherance to the rules in a package this simple would probably be overkill.
* If you're having issues LET ME KNOW.