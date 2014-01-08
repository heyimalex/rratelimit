from .utils import LimiterTestBase
from rratelimit import ListLimiter

class TestListLimiter(LimiterTestBase):
    def __init__(self):
        super(TestListLimiter,self).__init__(ListLimiter)