import unittest

from src.config import Config


class TestConfig(unittest.TestCase):
    def test_get_config(self):
        config_values = Config.get_config()
        expected_config = {
            "interarrival_time": 5,
            "kitchen_service_time": 3,
            "counter_service_time": 1,
            "kitchen_servers": 2,
            "counter_servers": 1,
            "kitchen_queue_size": 5,
            "counter_queue_size": 3,
            "warm_up_time": 60,
            "sim_duration": 480,
            "num_runs": 50,
            "mean_order_time": 2,
            "mean_cook_time": 5,
            "mean_service_time": 4,
            "driver_capacity": 10,
        }
        self.assertEqual(len(config_values), len(expected_config))
        for key, value in expected_config.items():
            print(key, value, key in config_values)
            self.assertTrue(key in config_values)
            self.assertEqual(config_values[key], value)


if __name__ == "__main__":
    unittest.main()
