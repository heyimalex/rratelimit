rratelimit
==========

General purpose rate limiting classes that work with redis and redis-py.

Installation
~~~~~~~~~~~~

Install via pip

::

    pip install rratelimit

Install from source

::

    git clone git://github.com/HeyImAlex/rratelimit.git
    cd rratelimit
    python setup.py install

**requires redis-server >= 2.6.0 to work properly**

Usage
~~~~~

In plain english, a limiter allows you to

::

    Limit {actor} from doing {action} {limit} times per {period} seconds

Each limiter shares the same basic interface:

-  constructor params

   -  **redis** - redis-py Redis or StrictRedis instance
   -  **action** (string) - Name for the action this limiter will limit
   -  **limit** (int) - Inclusive number of times you'd like ``action`` to be able to be executed per ``period`` seconds
   -  **period** (double) - Time window (in seconds) in which you want to limit ``action``. Reliable down to milliseconds (0.001).

-  methods

   -  **check** (``actor``): Return whether ``actor`` is over the limit for this action.
   -  **insert** (``actor``): Let the limiter know that ``actor`` has just completed this action.
   -  **checked\_insert** (``actor``): Convenience method for atomically checking if an actor is over the limit and, if they're not, running the insert method. Returns True if the insert suceeded, False if the user was over the limit.
   -  **check_ex** (``actor``, ``limit``, ``period``): (Only for ``ListLimiter``) Like ``check`` but can be called with lower limit or period (e.g for a 10/h limit, you can check also for 5/15m or 2/m limits).

Every method is atomic and thread safe. Internally rratelimit uses Lua scripts with redis' EVALSHA command for the bulk of the work, so it's fairly fast as well.

Example
-------

Say you're writing forum software in Flask and you want to limit your users to only be able to create a thread once every five minutes. Outside of any request context, create an instance of Limiter with the proper parameters. In this case the ``action`` would be something like ``"new_thread"``, the ``limit`` would be ``1``, and the ``period`` would be ``5*60``.

.. code:: python


    from redis import StrictRedis
    from rratelimit import Limiter

    r = StrictRedis(...)
    thread_limiter = Limiter(r, action='new_thread', limit=1, period=5*60)

Now in your view function all you need to do is call ``checked_insert`` whenever a user attempts to create a new thread. If it returns True, you know that the user was not over the limit and you can proceed to create the thread.

.. code:: python


    @app.route('/new_thread', methods=['GET', 'POST'])
    def new_thread():
        form = NewThreadForm(request.form)
        if request.method == 'POST' and form.validate():
            # Do some stuff
            if thread_limiter.checked_insert(request.remote_addr):
                # Create the thread
            else:
                # You were over the limit!

Boom.

Classes
~~~~~~~

Internally rratelimit has a few different Limiter classes. The default (and the one that's created when you call Limiter) is the ListLimiter, and for the vast vast vast vast *vast* majority of cases it'll do just fine.

However, in the name of completeness I've included a few more limiters (with perhaps even more to come). Following is a description of each of these limiters along with details of their implementations and their respective pros and cons.

ListBasedLimiter
----------------

-  **pros** - simple, very accurate, O(1) insert time, generally O(1) check time. Also a `check_ex` method exists to check for lower limits.
-  **cons** - potentially O(N) check time, memory usage, where N is the number of insertions made (over a certain threshold), could eat up a lot of memory with very large ``limit`` values or many inserts

The ListBasedLimiter works by LPUSHing a timestamp onto a list every time insert is called. It checks the limit by calling ``LINDEX {limit}`` and seeing if the returned value is greater than ``current_timestamp - period``. Check also LTRIMs all items past ``limit``, ensuring that after a check the list is at most ``limit`` keys long. Expiration is handled by setting a ttl equal to ``period`` on insert.

If you solely use checked\_insert on a ListBasedLimiter, you're guaranteed to LTRIM no more than one element per run, which makes it constant time. If you use check and insert separately, the bound for check is *technically* O(N).

**Note**: There is an edge case where ListBasedLimiters can leak memory; if you continually insert before the key expires without ever calling check, the list will never be trimmed. This trade off is made to maintain O(1) insert time.

HashBasedLimiter
----------------

-  **pros** - O(1) inserts, checks, and memory usage
-  **cons** - complicated, inherently inaccurate, constant big-O benefits sometimes negated by size of constant if you still need great accuracy on a long period.

The HashBasedLimiter is more complicated. It takes an additional constructor param, ``accuracy``, which basically defines a speed/accuracy tradeoff;

-  acceptable error = period/accuracy seconds
-  O(1) insert/check/memory where the constant is proportional to accuracy

The HashBasedLimiter internally works by creating ``2*accuracy`` "time buckets" arranged in a circle. Each time bucket represents ``period/accuracy`` seconds, and the current bucket is found by taking the current timestamp, dividing it by the bucket width, and then computing the modulo with the total number of buckets. When insert is called, the limiter finds the current bucket and INCRs it, clears half of the buckets in front of it (up to where the period starts), and sets an expire time equal to ``period``. When check is called, the limiter just adds up the contents of the bucket and half of the total buckets behind it.

The main takeaway here is that memory footprint, check times and insert times all scale with the accuracy parameter. If you don't need great accuracy and your ``limit`` is high, the HashBasedLimiter may be better suited for your usecase. If you *really* don't need great accuracy, the SimpleLimiter is likely a better match.

SimpleLimiter
-------------

-  **pros** - very low memory footprint (at most 2 keys per actor), very fast, very simple, good enough for many situations
-  **cons** - very inaccurate; allows up to 2x ``limit`` to be executed in short period of time.

The SimpleLimiter is... very simple. It just INCRs a key on insert and then checks if the contents of the current key are greater than or equal to ``limit``. The current key is found by dividing the current timestamp by ``period`` and taking the modulo of that with 3. Expiration is set on insertion to ``period``.

The important thing to know is that this isn't a "moving window" limiter; it doesn't make the guarantee that an actor can't make more than ``limit`` calls in the last ``period`` seconds, just that an actor can't make more than ``limit`` calls in period ``x``. This type of limiting is commonly found on web APIs (Twitter) and is might be better handled by your web server, but hey, it's here if you need it.

Race conditions
~~~~~~~~~~~~~~~

Sometimes you may want to chain multiple inserts or checks in an atomic way. Using locks is cumbersome and comes with overhead, so rratelimit provides an alternative through redis-py's pipelines.

Just create a pipeline and then call the limiter method you want with the pipeline object as the second parameter.

.. code:: python

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

TODO
~~~~

-  Work on benchmarking

Faq/Misc
~~~~~~~~

-  Huge thanks to /u/iminurnamez for coming up with checked\_insert as the name for checked\_insert. Naming things is tough...

-  I'm open to changing the verbage of the API while this project is young if you can come up with anything more elegant/intuitive than I've got.

-  Running check and insert separately to see if an actor can do an action creates a race condition; if another check is initiated before the insert is run, both checks could return False. Use the atomic checked\_insert method to prevent this.

-  Because redis is single threaded, every limiter method blocks while it's executing. HashBasedLimiters that take a long time to execute make all types of weird stuff happen. List based limiters still work fairly well. In general this shouldn't ever be a problem.

-  Don't do anything stupid: rratelimit might not catch it and you'll end up getting an incomprehensible error from the Lua interpreter.

-  Actions and actors should probably only contain letters, numbers, periods, dashes and underscores. I can't think of a situation where something bad would happen with strange keys, but I'd maybe play it safe. I'll look into this...

-  Keys are generally of the form ``rratelimit:{action}:{actor}``. It goes without saying that you shouldn't make keys that start with 'rratelimit' in other places in your application.

-  Hiredis with rratelimit is supported by simply downloading the package, but won't provide much in the way of speed increases as not a whole lot of data is being passed back and forth.

-  Redis-server 2.6.0+ required for EVALSHA and PEXPIRE

If you have any issues or questions just let me know and I'll be glad to help.
