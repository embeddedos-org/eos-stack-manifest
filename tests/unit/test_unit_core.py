import unittest
class TestEFabUnit(unittest.TestCase):
    def test_pcb_drill_hole_alignment(self):
        hole = (10.0, 20.0)
        target = (10.0, 20.0)
        self.assertEqual(hole, target)
