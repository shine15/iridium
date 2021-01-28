from collections import namedtuple

PivotPoint = namedtuple('PivotPoint', 'pp r1 s1 r2 s2 r3 s3')


def standard_pivot_pts(close, high, low):
    """
     calculate standard pivot points
    :param close:
    :param high:
    :param low:
    :return: PivotPoint pp - pivot point, r1 - 1st resistance, s1 - 1st support,
    r2 - 2nd resistance, s2 - 2nd support, r3 - 3rd resistance, s3 - 3rd support
    """
    pp = (high + low + close) / 3
    r1 = 2 * pp - low
    s1 = 2 * pp - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)
    r3 = high + 2 * (pp - low)
    s3 = low - 2 * (high - pp)
    return PivotPoint(pp, r1, s1, r2, s2, r3, s3)
