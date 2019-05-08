
import unittest

from vstring.version_string import VersionString, InvalidComparisonError

class TestVersionStrings(unittest.TestCase):

    def test_create_version_string(self):

        self.assertRaises(ValueError, VersionString, "1.2.h")

    def test_invalid_version_string(self):
        
        v1 = VersionString("1.0.9")
        v2 = "65" # normal string

        self.assertRaises(InvalidComparisonError, v1.__eq__, v2)

    def test2_invalid_version_string(self):
        
        v1 = VersionString("1.8.0")
        v2 = "1.8.1" # string that looks like a version string

        self.assertRaises(InvalidComparisonError, v1.__eq__, v2)

    def test1_equal(self):
        v1 = VersionString("1.2.4")
        v2 = VersionString("1.2.4")

        self.assertTrue(v1 == v2)

    def test2_less_than(self):
        v1 = VersionString("1.2.3")
        v2 = VersionString("1.2.4")

        self.assertTrue(v1 < v2)

    def test3_greater_than(self):
        v1 = VersionString("1.2.5")
        v2 = VersionString("1.2.0")

        self.assertTrue(v1 > v2)

    def test4_not_equal(self):
        v1 = VersionString("1.2.4")
        v2 = VersionString("1.2")

        self.assertTrue(v1 != v2)

    def test5_not_equal(self):
        v1 = VersionString("1.2.4")
        v2 = VersionString("1.2.4.0")

        self.assertTrue(v1 != v2)

    def test6__less_than(self):
        v1 = VersionString("1.2.4")
        v2 = VersionString("1.2.4.0")

        self.assertTrue(v1 < v2)

    def test7__less_than(self):
        v1 = VersionString("1.2.4")
        v2 = VersionString("1.2.4")

        self.assertFalse(v1 < v2)

    def test8__greater_than(self):
        v1 = VersionString("1.2.8.8.9.4")
        v2 = VersionString("1.2.8.8.9.4")

        self.assertFalse(v1 > v2)

    def test9__greater_than(self):
        v1 = VersionString("3")
        v2 = VersionString("1")

        self.assertTrue(v1 > v2)

    def test10__equal(self):
        v1 = VersionString("3.01.4")
        v2 = VersionString("3.1.4")

        self.assertTrue(v1 == v2)

    def test11__equal(self):
        v1 = VersionString("3.01.4")
        v2 = VersionString("3.1.04")

        self.assertTrue(v1 == v2)

    def test12__not_equaL(self):
        v1 = VersionString("3.01.40")
        v2 = VersionString("3.1.4")

        self.assertTrue(v1 != v2)

    
if __name__ == "__main__":
    unittest.main()