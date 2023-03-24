
import unittest
from src import config


class TestConfig(unittest.TestCase):
    def test_default_config(self):
        expected_config = {'n_customers': 100, 'sim_time': 3600, 'n_cashiers': 2}
        self.assertEqual(config.get_config(), expected_config)


if __name__ == '__main__':
    unittest.main()
