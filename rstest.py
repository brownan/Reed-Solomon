import unittest

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

if __name__ == "__main__":
    unittest.main()
