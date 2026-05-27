import unittest

class TesteFabFunctional(unittest.TestCase):
    def test_pick_and_place_nozzle_pipeline(self):
        feeder = ["MCU_STM32", "RES_10K", "CAP_100NF"]
        board_slots = []
        # Pick MCU
        part = feeder.pop(0)
        assert part == "MCU_STM32"
        # Place MCU on board
        board_slots.append(part)
        assert len(board_slots) == 1
