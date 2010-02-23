class Polynomial(object):
    """Polynomial objects are immutable"""
    def __init__(self, coefficients):
        """Creates a new polynomial object with the given coefficients.
        Coefficients are given with the hightest order term first.
        Each coefficient should be an integer
        """
        c = list(coefficients)
        while c and c[0] == 0:
            c.pop(0)
        if not c:
            c.append(0)
        self.coefficients = tuple(c)

    def __len__(self):
        """Returns the number of terms in the polynomial"""
        return len(self.coefficients)

    def __add__(self, other):
        diff = len(self) - len(other)
        if diff > 0:
            t1 = self.coefficients
            t2 = (0,) * diff + other.coefficients
        else:
            t1 = (0,) * (-diff) + self.coefficients
            t2 = other.coefficients

        return Polynomial(x+y for x,y in zip(t1, t2))

    def __neg__(self):
        return Polynomial(-x for x in self.coefficients)
    def __sub__(self, other):
        return self + -other
            
    def __mul__(self, other):
        terms = [0] * (len(self) + len(other))

        for i1, c1 in enumerate(reversed(self.coefficients)):
            for i2, c2 in enumerate(reversed(other.coefficients)):
                terms[i1+i2] += c1*c2

        return Polynomial(reversed(terms))

    def __floordiv__(self, other):
        return divmod(self, other)[0]
    def __mod__(self, other):
        return divmod(self, other)[1]
    def __divmod__(self, other):
        # See how many times the highest order term
        # of other can go into the highest order term of self

        # "self"
        dividend_power = len(self) - 1
        dividend_coefficient = self.coefficients[0]

        # "other"
        divisor_power = len(other) - 1
        divisor_coefficient = other.coefficients[0]

        quotient_power = dividend_power - divisor_power
        if quotient_power < 0:
            return Polynomial((0,)), self
        quotient_coefficient = 1.0 * dividend_coefficient / divisor_coefficient
        quotient = Polynomial( (quotient_coefficient,) + (0,) * quotient_power )

        remander = self - quotient * other

        if remander.coefficients == (0,):
            return quotient, remander

        morequotient, remander = divmod(remander, other)
        return quotient + morequotient, remander

    def __eq__(self, other):
        return self.coefficients == other.coefficients
    def __ne__(self, other):
        return self.coefficients != other.coefficients
    def __hash__(self):
        return hash(self.coefficients)

    def __repr__(self):
        n = self.__class__.__name__
        return "%s(%r)" % (n, self.coefficients)
    def __str__(self):
        buf = StringIO()
        l = len(self) - 1
        for i, c in enumerate(self.coefficients):
            if not c and i > 0:
                continue
            power = l - i
            if power > 1:
                buf.write("%sx^%s" % (c, power))
            elif power == 1:
                buf.write("%sx" % c)
            else:
                buf.write("%s" % c)
            buf.write(" + ")
        return buf.getvalue()[:-3]
