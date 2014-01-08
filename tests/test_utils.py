from rratelimit.utils import dtime

def test_dtime():
    assert dtime(0, 10, 1) == 0
    assert dtime(0.99, 10, 1) == 0
    assert dtime(1, 10, 1) == 1
    assert dtime(11, 10, 1) == 1
    assert dtime(1, 10, .5) == 2
    assert dtime(1.49, 10, .5) == 2