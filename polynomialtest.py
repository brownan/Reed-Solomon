import unittest

from ff import Polynomial

class TestPolynomial(unittest.TestCase):
    def test_add_1(self):
        one = Polynomial((2,4,7,3))
        two = Polynomial((5,2,4,2))

        r = one + two

        self.assertEqual(r.coefficients, (7, 6, 11, 5))

    def test_add_2(self):
        one = Polynomial((2,4,7,3,5,2))
        two = Polynomial((5,2,4,2))

        r = one + two

        self.assertEqual(r.coefficients, (2,4,12,5,9,4))

    def test_add_3(self):
        one = Polynomial((7,3,5,2))
        two = Polynomial((6,8,5,2,4,2))

        r = one + two

        self.assertEqual(r.coefficients, (6,8,12,5,9,4))

    def test_mul_1(self):
        one = Polynomial((2,4,7,3))
        two = Polynomial((5,2,4,2))

        r = one * two

        self.assertEqual(r.coefficients,
                (10,24,51,49,42,26,6))

    def test_div_1(self):
        one = Polynomial((1,4,0,3))
        two = Polynomial((1,0,1))

        q, r = divmod(one, two)
        self.assertEqual(q, one // two)
        self.assertEqual(r, one % two)

        self.assertEqual(q.coefficients, (1,4))
        self.assertEqual(r.coefficients, (-1,-1))

    def test_div_2(self):
        one = Polynomial((1,0,0,2,2,0,1,2,1))
        two = Polynomial((1,0,-1))

        q, r = divmod(one, two)
        self.assertEqual(q, one // two)
        self.assertEqual(r, one % two)

        self.assertEqual(q.coefficients, (1,0,1,2,3,2,4))
        self.assertEqual(r.coefficients, (4,5))

    def test_div_3(self):
        # 0 quotient
        one = Polynomial((1,0,-1))
        two = Polynomial((1,1,0,0,-1))

        q, r = divmod(one, two)
        self.assertEqual(q, one // two)
        self.assertEqual(r, one % two)

        self.assertEqual(q.coefficients, (0,))
        self.assertEqual(r.coefficients, (1,0,-1))

    def test_div_4(self):
        # no remander
        one = Polynomial((1,0,0,2,2,0,1,-2,-4))
        two = Polynomial((1,0,-1))

        q, r = divmod(one, two)
        self.assertEqual(q, one // two)
        self.assertEqual(r, one % two)

        self.assertEqual(q.coefficients, (1,0,1,2,3,2,4))
        self.assertEqual(r.coefficients, (0,))

if __name__ == "__main__":
    unittest.main()
