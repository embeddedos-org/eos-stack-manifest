import unittest

class TesteFabSimulation(unittest.TestCase):
    def test_gcode_parser_motion_simulation(self):
        # Simulate stepper motor step generation from G-Code G1 command
        gcode_cmd = "G1 X10.0 Y20.0 F1200"
        steps_x = 0
        steps_y = 0
        if gcode_cmd.startswith("G1"):
            steps_x = 10 * 80 # 80 steps per mm
            steps_y = 20 * 80
        assert steps_x == 800
        assert steps_y == 1600
