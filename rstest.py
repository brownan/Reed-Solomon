import unittest

import rs

class TestRS(unittest.TestCase):
    def test_one(self):
        code = rs.encode("Hello, world!")

        self.assertTrue(rs.verify(code))

    def test_two(self):
        """Verifies that changing any single character will invalidate the
        codeword"""
        code = rs.encode("Hello, world!")

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

if __name__ == "__main__":
    unittest.main()
