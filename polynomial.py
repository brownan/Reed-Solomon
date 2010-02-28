from StringIO import StringIO

class Polynomial(object):
    """Polynomial objects are immutable"""
    def __init__(self, coefficients):
        """Creates a new polynomial object with the given coefficients.
        Coefficients are given with the hightest order term first.
        Each coefficient should be an integer
        """
        c = list(coefficients)
        # Expunge any leading 0 coefficients
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
            if c1 == 0:
                # Optimization
                continue
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
            # Doesn't divide at all, return 0 for the quotient and the entire
            # dividend as the remander
            return Polynomial((0,)), self

        # Compute how many times the highest order term in the divisor goes
        # into the dividend
        quotient_coefficient = dividend_coefficient / divisor_coefficient
        quotient = Polynomial( (quotient_coefficient,) + (0,) * quotient_power )

        remander = self - quotient * other

        if remander.coefficients == (0,):
            # Goes in evenly with no remainder, we're done
            return quotient, remander

        # There was a remander, see how many times the remainder goes into the
        # divisor
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
            if c == 1 and power != 0:
                c = ""
            if power > 1:
                buf.write("%sx^%s" % (c, power))
            elif power == 1:
                buf.write("%sx" % c)
            else:
                buf.write("%s" % c)
            buf.write(" + ")
        return buf.getvalue()[:-3]

    def evaluate(self, x):
        """Evaluate this polynomial at value x, returning the result.  To be
        completely general, this method is written to explicitly do each
        calculation, taking O(n) time where n is len(self)
        """
        # Holds the sum over each term in the polynomial
        c = 0

        # Holds the current power of x. This is multiplied by x after each term
        # in the polynomial is added up.
        p = 1

        for term in reversed(self.coefficients):
            c = c + term * p

            p = p * x

        return c
