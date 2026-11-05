import unittest

from openfga_sdk import api_client
from openfga_sdk.oauth2_common import jitter
from openfga_sdk.sync import api_client as sync_api_client


class TestBackoff(unittest.TestCase):
    """The retry wait helpers accept a minimum wait of 0"""

    def test_random_time_with_zero_min_wait(self):
        for loop_count in range(3):
            self.assertEqual(api_client.random_time(loop_count, 0), 0)
            self.assertEqual(sync_api_client.random_time(loop_count, 0), 0)

    def test_random_time_stays_in_range(self):
        for loop_count in range(3):
            for random_time in (api_client.random_time, sync_api_client.random_time):
                wait = random_time(loop_count, 100)
                self.assertGreaterEqual(wait, 2**loop_count * 100 / 1000)
                self.assertLess(wait, 2 ** (loop_count + 1) * 100 / 1000)

    def test_jitter_with_zero_min_wait(self):
        for loop_count in range(3):
            self.assertEqual(jitter(loop_count, 0), 0)


if __name__ == "__main__":
    unittest.main()
