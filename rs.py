# encoding: UTF-8
from ff import GF256int
from polynomial import Polynomial

"""This module implements Reed-Solomon Encoding.
Specifically, RS(255,223), 223 data bytes and 32 parity bytes

Warning: Because of the way I've implemented things, leading null bytes in a
message are dropped. Be careful if encoding binary data.
"""

# Constants (do not change)
n = 255
k = 223

# Generate the generator polynomial for RS codes
# g(x) = (x-α^1)(x-α^2)...(x-α^32)
# α is 3, a generator for GF(2^8)
g = Polynomial((GF256int(1),))
for alpha in xrange(1,n-k+1):
    p = Polynomial((GF256int(1), GF256int(3)**alpha))
    g = g * p

# h(x) = (x-α^33)(x-α^34)...(x-α^255)
h = Polynomial((GF256int(1),))
for alpha in xrange(n-k+1,n+1):
    p = Polynomial((GF256int(1), GF256int(3)**alpha))
    h = h * p

# g*h is used in verification, and is always x^255-1 when n=255
gtimesh = Polynomial(x255=GF256int(1), x0=GF256int(1))

def encode(message, poly=False):
    """Encode a given string with reed-solomon encoding. Returns a byte
    string with 32 parity bytes at the end.
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

def decode(r):
    """Given a received byte string r, attempts to decode it. If it's a valid
    codeword, or if there are less than 2s errors, the message is returned
    """
    #if verify(r):
    #    # The last 32 bytes are parity
    #    return r[:-32]

    # Turn r into a polynomial
    r = Polynomial(GF256int(ord(x)) for x in r)

    # Compute the syndromes:
    sz = _syndromes(r)

    # Find the error locator polynomial and error evaluator polynomial using
    # the Berlekamp-Massey algorithm
    sigma, omega = _berlekamp_massey(sz)
    print "sigma=%s" % sigma
    print "omega=%s" % omega

    # Now use Chien's procedure to find the error locations
    X, j = _chien_search(sigma)
    print "X=%s" % X
    print "j=%s" % j

    # And finally, find the error magnitudes with Forney's Formula
    Y = _forney(omega, X)
    print "Y=%s" % Y

    # Put the error and locations together to form the error polynomial
    Elist = []
    for i in xrange(255):
        if i in j:
            Elist.append(Y[j.index(i)])
        else:
            Elist.append(GF256int(0))
    E = Polynomial(reversed(Elist))
    print "E=%s" % E

    # And we get our real codeword!
    c = r - E

    # Form it back into a string and return all but the last 32 bytes
    return "".join(chr(x) for x in c.coefficients)[:-32]


def _syndromes(r):
    """Given the received codeword r in the form of a Polynomial object,
    computes the syndromes and returns the syndrome polynomial
    """
    # s[l] is the received codeword evaluated at α^l for 1 <= l <= s
    # α in this implementation is 3
    s = [GF256int(0)] # s[0] is 0 (coefficient of z^0)
    for l in xrange(1, n-k+1):
        s.append( r.evaluate( GF256int(3)**l ) )

    # Now build a polynomial out of all our s[l] values
    # s(z) = sum(s_i * z^i, i=1..inf)
    sz = Polynomial( reversed( s ) )

    return sz

def _berlekamp_massey(s):
    """Computes and returns the error locator polynomial (sigma) and the error
    evaluator polynomial (omega)
    The parameter s is the syndrome polynomial (syndromes encoded in a
    generator function)

    Notes:
    The error polynomial:
    E(x) = E_0 + E_1 x + ... + E_(n-1) x^(n-1)

    j_1, j_2, ..., j_s are the error positions. (There are at most s errors)

    Error location X_i is defined: X_i = α^(j_i)
    that is, the power of α corresponding to the error location

    Error magnitude Y_i is defined: E_(j_i)
    that is, the coefficient in the error polynomial at position j_i

    Error locator polynomial:
    sigma(z) = Product( 1 - X_i * z, i=1..s )
    roots are the reciprocals of the error locations
    ( 1/X_1, 1/X_2, ...)

    Error evaluator polynomial omega(z) not written here
    """
    # Initialize:
    sigma =  [ Polynomial((GF256int(1),)) ]
    omega =  [ Polynomial((GF256int(1),)) ]
    tao =    [ Polynomial((GF256int(1),)) ]
    gamma =  [ Polynomial((GF256int(0),)) ]
    D =      [ 0 ]
    B =      [ 0 ]

    # Polonomial constants:
    ONE = Polynomial(z0=GF256int(1))
    ZERO = Polynomial(z0=GF256int(0))
    Z = Polynomial(z1=GF256int(1))
    
    # Iteratively compute the polynomials 2s times. The last ones will be
    # correct
    for l in xrange(0, 32):
        # Goal for each iteration: Compute sigma[l+1] and omega[l+1] such that
        # (1 + s)*sigma[l] == omega[l] in mod z^(l+1)

        # For this particular loop iteration, we have sigma[l] and omega[l],
        # and are computing sigma[l+1] and omega[l+1]
        
        # First find Delta, the non-zero coefficient of z^(l+1) in
        # (1 + s) * sigma[l]
        # This delta is valid for l (this iteration) only
        Delta = ( (ONE + s) * sigma[l] ).get_coefficient(l+1)
        # Make it a polynomial of degree 0
        Delta = Polynomial(x0=Delta)

        # Can now compute sigma[l+1] and omega[l+1] from
        # sigma[l], omega[l], tao[l], gamma[l], and Delta
        sigma.append(
                sigma[l] - Delta * Z * tao[l]
                )
        omega.append(
                omega[l] - Delta * Z * gamma[l]
                )

        # Now compute the next tao and gamma
        # There are two ways to do this
        if Delta == ZERO or 2*D[l] > (l+1):
            # Rule A
            D.append( D[l] )
            B.append( B[l] )
            tao.append( Z * tao[l] )
            gamma.append( Z * gamma[l] )

        elif Delta != ZERO and 2*D[l] < (l+1):
            # Rule B
            D.append( l + 1 - D[l] )
            B.append( 1 - B[l] )
            tao.append( sigma[l] // Delta )
            gamma.append( omega[l] // Delta )
        elif 2*D[l] == (l+1):
            if B[l] == 0:
                # Rule A (same as above)
                D.append( D[l] )
                B.append( B[l] )
                tao.append( Z * tao[l] )
                gamma.append( Z * gamma[l] )

            else:
                # Rule B (same as above)
                D.append( l + 1 - D[l] )
                B.append( 1 - B[l] )
                tao.append( sigma[l] // Delta )
                gamma.append( omega[l] // Delta )
        else:
            raise Exception("Code shouldn't have gotten here")


    print "sigmas:"
    for s in sigma:
        print "  %s" % s
    print "omegas:"
    for o in omega:
        print "  %s" % o
    return sigma[-1], omega[-1]

def _chien_search(sigma):
    """Recall the definition of sigma, it has s (16) roots. To find them,
    this function evaluates sigma at all 255 non-zero points to find the roots
    The inverse of the roots are X_i, the error locations

    Returns a list X of error locations, and a corresponding list j of error
    positions (the discrete log of the corresponding X value)
    The lists are up to s (16) elements large.
    """
    X = []
    j = []
    p = GF256int(3)
    for l in xrange(1,256):
        # These evaluations could be more efficient, but oh well
        if sigma.evaluate( p**l ) == 0:
            X.append( p**(-l) )
            # This is different than the notes, I think the notes were in error
            # Notes said j values were just l, when it's actually 255-l
            j.append(255 - l)

    return X, j

def _forney(omega, X):
    """Computes the error magnitudes"""
    Y = []

    for l, Xl in enumerate(X):
        # Compute the first part of Yl
        Yl = Xl**16
        Yl *= omega.evaluate( Xl.inverse() )
        Yl *= Xl.inverse()

        # Compute the sequence product and multiply its inverse in
        prod = GF256int(1)
        for ji in xrange(16):
            if ji == l:
                continue
            if ji < len(X):
                Xj = X[ji]
            else:
                Xj = GF256int(0)
            prod = prod * (Xl - Xj)
        Yl = Yl * prod.inverse()

        Y.append(Yl)
    return Y
