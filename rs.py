# encoding: UTF-8
from ff import GF256int
from polynomial import Polynomial

"""This module implements Reed-Solomon Encoding.
Specifically, RS(255,223), 223 data bytes and 32 parity bytes
"""

n = 255
k = 223

# Generate the generator polynomial for RS codes
# g(x) = (x-α^0)(x-α^1)...(x-α^254)
# α is 3, a generator for GF(2^8)
g = Polynomial((GF256int(1),))
for alpha in xrange(1,n-k+1):
    p = Polynomial((GF256int(1), GF256int(3)**alpha))
    #print "Multiplying in %s" % p
    g = g * p
    #print "\tGot %s" % g

#print "g is %s\nComputing h..." % g

h = Polynomial((GF256int(1),))
for alpha in xrange(n-k+1,n+1):
    p = Polynomial((GF256int(1), GF256int(3)**alpha))
    #print "Multiplying in %s" % p
    h = h * p
    #print "\tGot %s" % g
#print "h is %s" % h

# g*h is used in verification, and is always x^255+1 when n=255
gtimesh = Polynomial((GF256int(1),) + (GF256int(0),)*(n-1) + (GF256int(1),))

def encode(message, poly=False):
    """Encode a given string with reed-solomon encoding. Returns a byte
    stream with 32 parity bytes at the end.
    If poly is not False, returns the encoded Polynomial object instead of
    the polynomial translated back to a string
    """
    if len(message)>k:
        raise ValueError("Message length is max %d. Message was %d" % (k,
            len(message)))

    # Encode message as a polynomial:
    m = Polynomial(GF256int(ord(x)) for x in message)

    # Shift polynomial up by n-k (32) by multiplying by x^32
    mprime = m * Polynomial((GF256int(1),) + (GF256int(0),)*(n-k))

    # mprime = q*g + b for some q
    # so let's find b:
    b = mprime % g

    # Subtract out b, so now c = q*g
    c = mprime - b
    # Since c is a multiple of g, it has (at least) n-k roots: α^1 through
    # α^(n-k)

    if poly:
        return c

    # Turn the polynomial c back into a byte string
    return "".join(chr(x) for x in c.coefficients)

def verify(code):
    """Verifies the code is valid by testing that the code as a polynomial code
    divides g
    returns True/False
    """
    c = Polynomial(GF256int(ord(x)) for x in code)
    # Not sure what I was thinking with this, it still works...
    #return (c*h)%gtimesh == Polynomial((0,))

    # ...But since all codewords are multiples of g, checking that code divides
    # g should suffice for validating a codeword.
    return c % g == Polynomial((0,))

