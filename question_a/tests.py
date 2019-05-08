
import unittest

from coordinates_comparator import overlaps


class OverlapTest(unittest.TestCase):
    
    def test1_overl(self):
        self.assertTrue(overlaps((1,5), (2,6)))

    def test2_overlap(self):
        self.assertTrue(overlaps((-1,5), (5,0)))

    def test3_overlap(self):
        self.assertTrue(overlaps((5,-1), (0,5)))

    def test4_overlap(self):
        self.assertTrue(overlaps((0,0), (0,0)))
    
    def test5_overlap(self):
        self.assertTrue(overlaps((20.2,20), (20.1,20)))

    def test6_overlap(self):
        self.assertTrue(overlaps((9,-44), (-23,67)))

    def test7_overlap(self):
        self.assertTrue(overlaps((-9000,4), (0,-19)))

    def test8_overlap(self):
        self.assertTrue(overlaps((60,-6), (-6,6)))

    def test9_not_overlap(self):
        self.assertFalse(overlaps((1,5), (6,8)))
    
    def test10_not_overlap(self):
        self.assertFalse(overlaps((-5,-2), (3, -1)))

    def test11_not_overlap(self):
        self.assertFalse(overlaps((0,0), (1,1)))

    def test12_not_overlap(self):
        self.assertFalse(overlaps((8,-45), (9,33)))

    def test13_not_overlap(self):
        self.assertFalse(overlaps((-3,-11), (-12,-20)))

    def test14_not_overlap(self):
        self.assertFalse(overlaps((9.5,6.1), (6,-6.44)))

    def test15_not_overlap(self):
        self.assertFalse(overlaps((1,0.0), (1.1,8)))

    def test16_not_overlap(self):
        self.assertFalse(overlaps((-5.5,-34), (9,-1)))


if __name__ == "__main__":
    unittest.main()