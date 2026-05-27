import unittest

class TesteFabUnit(unittest.TestCase):
    def test_pcb_drill_hole_alignment(self):
        # Simulate PCB drilling machine coordinate alignment
        drill_target = (10.50, 20.00)
        drill_head = (10.49, 20.01)
        error_x = abs(drill_target[0] - drill_head[0])
        error_y = abs(drill_target[1] - drill_head[1])
        assert error_x < 0.02, "PCB drill X alignment error exceeds 0.02mm tolerance"
        assert error_y < 0.02, "PCB drill Y alignment error exceeds 0.02mm tolerance"
