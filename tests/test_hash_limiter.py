from .utils import LimiterTestBase
from rratelimit import HashLimiter

class TestHashLimiter(LimiterTestBase):
    def __init__(self):
        super(TestHashLimiter,self).__init__(HashLimiter, accuracy=50)