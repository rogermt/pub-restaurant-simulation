"""
Tests for the simulation runner and related functionality.
"""

import unittest
from unittest.mock import patch

from src.restaurant import Restaurant
from src.simulation import SimulationConfig, SimulationRunner


class TestSimulationConfig(unittest.TestCase):
    """Test the SimulationConfig class."""

    def test_default_config(self):
        """Test that default configuration values are set correctly."""
        config = SimulationConfig()

        self.assertEqual(config.duration, 480)
        self.assertEqual(config.interarrival_time, 5.0)
        self.assertEqual(config.kitchen_servers, 2)
        self.assertEqual(config.counter_servers, 1)
        self.assertEqual(config.num_runs, 1)

    def test_custom_config(self):
        """Test that custom configuration values are set correctly."""
        config = SimulationConfig(
            duration=120,
            interarrival_time=10.0,
            kitchen_servers=3,
            counter_servers=2,
            num_runs=5,
        )

        self.assertEqual(config.duration, 120)
        self.assertEqual(config.interarrival_time, 10.0)
        self.assertEqual(config.kitchen_servers, 3)
        self.assertEqual(config.counter_servers, 2)
        self.assertEqual(config.num_runs, 5)


class TestSimulationRunner(unittest.TestCase):
    """Test the SimulationRunner class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = SimulationConfig(duration=60, interarrival_time=30.0)
        self.runner = SimulationRunner(self.config)

    def test_initialization(self):
        """Test that SimulationRunner initializes correctly."""
        self.assertEqual(self.runner.config, self.config)

    def test_run_simulation_returns_restaurant_and_metrics(self):
        """Test that run_simulation returns restaurant and metrics."""
        restaurant, metrics = self.runner.run_simulation(duration=30, verbose=False)

        # Check that we get a restaurant instance
        self.assertIsInstance(restaurant, Restaurant)

        # Check that metrics is a dictionary with expected keys
        self.assertIsInstance(metrics, dict)
        self.assertIn("simulation_duration", metrics)
        self.assertIn("total_customers_served", metrics)
        self.assertIn("customers_per_hour", metrics)
        self.assertIn("kitchen_utilization", metrics)
        self.assertIn("counter_utilization", metrics)

    def test_run_simulation_with_different_durations(self):
        """Test that simulation runs with different durations."""
        # Short simulation
        restaurant1, metrics1 = self.runner.run_simulation(duration=10, verbose=False)
        self.assertEqual(metrics1["simulation_duration"], 10)

        # Longer simulation
        restaurant2, metrics2 = self.runner.run_simulation(duration=60, verbose=False)
        self.assertEqual(metrics2["simulation_duration"], 60)

    def test_metrics_collection(self):
        """Test that metrics are collected correctly."""
        restaurant, metrics = self.runner.run_simulation(duration=30, verbose=False)

        # Check that customer counts are non-negative integers
        self.assertGreaterEqual(metrics["total_customers_served"], 0)
        self.assertIsInstance(metrics["total_customers_served"], int)

        # Check that utilization percentages are between 0 and 100
        self.assertGreaterEqual(metrics["kitchen_utilization"], 0.0)
        self.assertLessEqual(metrics["kitchen_utilization"], 100.0)
        self.assertGreaterEqual(metrics["counter_utilization"], 0.0)
        self.assertLessEqual(metrics["counter_utilization"], 100.0)

    def test_customer_breakdown_in_metrics(self):
        """Test that customer breakdown is included in metrics."""
        restaurant, metrics = self.runner.run_simulation(duration=60, verbose=False)

        # Check that customer breakdown is present
        self.assertIn("inhouse_customers", metrics)
        self.assertIn("foodapp_customers", metrics)

        # Check that breakdown adds up to total
        total_breakdown = metrics["inhouse_customers"] + metrics["foodapp_customers"]
        self.assertEqual(total_breakdown, metrics["total_customers_served"])

    def test_run_multiple_simulations(self):
        """Test that multiple simulation runs work correctly."""
        num_runs = 3
        all_metrics = self.runner.run_multiple_simulations(
            num_runs=num_runs, verbose=False
        )

        # Check that we get the right number of results
        self.assertEqual(len(all_metrics), num_runs)

        # Check that each result has the expected structure
        for i, metrics in enumerate(all_metrics):
            self.assertIsInstance(metrics, dict)
            self.assertIn("run_number", metrics)
            self.assertEqual(metrics["run_number"], i + 1)
            self.assertIn("total_customers_served", metrics)

    def test_calculate_utilization(self):
        """Test the utilization calculation method."""
        # Test normal case
        utilization = self.runner._calculate_utilization(
            total_service_time=30.0, duration=60, num_servers=2
        )
        expected = (30.0 / (60 * 2)) * 100
        self.assertEqual(utilization, expected)

        # Test edge case: zero duration
        utilization_zero_duration = self.runner._calculate_utilization(
            total_service_time=30.0, duration=0, num_servers=2
        )
        self.assertEqual(utilization_zero_duration, 0.0)

        # Test edge case: zero servers
        utilization_zero_servers = self.runner._calculate_utilization(
            total_service_time=30.0, duration=60, num_servers=0
        )
        self.assertEqual(utilization_zero_servers, 0.0)

    @patch("builtins.print")
    def test_print_simulation_results(self, mock_print):
        """Test that simulation results are printed correctly."""
        metrics = {
            "simulation_duration": 60,
            "total_customers_served": 10,
            "customers_per_hour": 10.0,
            "kitchen_utilization": 50.0,
            "counter_utilization": 75.0,
            "inhouse_customers": 7,
            "foodapp_customers": 3,
        }

        self.runner._print_simulation_results(metrics)

        # Check that print was called (we don't need to verify exact output)
        self.assertTrue(mock_print.called)

    @patch("builtins.print")
    def test_print_aggregate_results(self, mock_print):
        """Test that aggregate results are printed correctly."""
        all_metrics = [
            {
                "total_customers_served": 10,
                "customers_per_hour": 10.0,
                "kitchen_utilization": 50.0,
                "counter_utilization": 75.0,
            },
            {
                "total_customers_served": 12,
                "customers_per_hour": 12.0,
                "kitchen_utilization": 60.0,
                "counter_utilization": 80.0,
            },
        ]

        self.runner._print_aggregate_results(all_metrics)

        # Check that print was called
        self.assertTrue(mock_print.called)


if __name__ == "__main__":
    unittest.main()
