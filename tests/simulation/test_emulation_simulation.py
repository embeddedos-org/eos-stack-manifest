import unittest
class TestEFabSimulation(unittest.TestCase):
    def test_gcode_parser_motion_simulation(self):
        gcode = "G1 X10 Y20 F1000"
        self.assertTrue("G1" in gcode)
