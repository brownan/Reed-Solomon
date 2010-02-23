from StringIO import StringIO

class GF28(int):
    """Instances of this object are elements of the field GF(2^8)
    Instances are integers in the range 0 to 255, and correspond
    to polynomials in Z_2[x] where each bit in the integer is a
    coefficient
    """
    # Maps integers to GF28 instances
    cache = {}
    # Maps pairs of integers to their product
    multcache = {}
    
    def __new__(cls, value):
        if value > 255 or value < 0:
            raise ValueError("Field elements of GF(2^8) are between 0 and 255")

        # Check cache
        try:
            return GF28.cache[value]
        except KeyError:
            newval = int.__new__(cls, value)
            GF28.cache[int(value)] = newval
            return newval

    def __add__(self, other):
        """Addition in GF(2^8) is the xor of the two
        """
        return GF28(self ^ other)
    __sub__ = __add__
    
    def __mul__(self, other):
        """Multiplication in GF(2^8)
        """

        # Check cache
        try:
            return GF28.multcache[self, other]
        except KeyError:
            pass
        try:
            return GF28.multcache[other, self]
        except KeyError:
            pass

        # peasant's algorithm (I think)
        p = int(self)
        b = int(other)
        r = 0
        while b:
            if b & 1:
                r = r ^ p
            b = b >> 1
            p = p << 1
            if p & 0x100:
                p = p ^ 0x11b

        GF28.multcache[int(self), int(other)] = GF28(r)
        return GF28(r)


class GF232(object):
    """Elements of this class represent elements of the field GF(2^32)
    """
    pass

