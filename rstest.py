import unittest
import itertools

import rs

class TestRSverify(unittest.TestCase):
    def test_one(self):
        """Tests a codeword without errors validates"""
        code = rs.encode("Hello, world!")

        self.assertTrue(rs.verify(code))

    def test_two(self):
        """Verifies that changing any single character will invalidate the
        codeword"""
        code = rs.encode("Hello, world! This is a test message, to be encoded,"
                " and verified.")

        for i, c in enumerate(code):
            # Change the value at position i and verify that the code is not
            # valid
            # Change it to a 0, unless it's already a 0
            if ord(c) == 0:
                c = chr(1)
            else:
                c = chr(0)
            bad_code = code[:i] + c + code[i+1:]

            self.assertFalse(rs.verify(bad_code))

class TestRSdecoding(unittest.TestCase):
    def setUp(self):
        self.string = "Hello, world! This is a long string"

        codestr = rs.encode(self.string)

        self.code = codestr

    def test_noerr(self):
        """Make sure a codeword with no errors decodes"""
        decode = rs.decode(self.code)
        self.assertEqual(self.string, decode)

    def test_oneerr(self):
        """Change just one byte and make sure it decodes"""
        for i, c in enumerate(self.code):
            newch = chr( (ord(c)+50) % 256 )
            r = self.code[:i] + newch + self.code[i+1:]

            decode = rs.decode(r)

            self.assertEqual(self.string, decode)

    def atest_twoerr(self):
        """Test every combination of 2 byte changes still decodes"""
        for i1, i2 in itertools.combinations(range(len(self.code)), 2):
            r = bytearray(self.code)

            # increment the byte by 50
            r[i1] = (r[i1] + 50) % 256
            r[i2] = (r[i2] + 50) % 256

            decode = rs.decode(r)
            self.assertEqual(self.string, decode)

    def test_16err(self):
        """Tests if 16 byte errors still decodes"""
        errors = [5, 6, 12, 13, 38, 40, 42, 47, 50, 57, 58, 59, 60, 61, 62, 65]
        r = bytearray(self.code)

        for e in errors:
            r[e] = (r[e] + 50) % 256

        decode = rs.decode(r)
        self.assertEqual(self.string, decode)

    def test_17err(self):
        """Kinda pointless, checks that 17 errors doesn't decode"""
        errors = [5, 6, 12, 13, 22, 38, 40, 42, 47, 50, 57, 58, 59, 60, 61, 62,
                65]
        r = bytearray(self.code)

        for e in errors:
            r[e] = (r[e] + 50) % 256

        decode = rs.decode(r)
        self.assertNotEqual(self.string, decode)


if __name__ == "__main__":
    unittest.main()
