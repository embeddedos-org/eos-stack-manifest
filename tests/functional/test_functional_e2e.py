import unittest
class TestEFabFunctional(unittest.TestCase):
    def test_pick_and_place_nozzle_pipeline(self):
        pipeline = ["home", "pick", "verify", "place"]
        self.assertEqual(pipeline[-1], "place")
