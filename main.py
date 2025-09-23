"""
Main entry point for the restaurant simulation.

This script provides a command-line interface for running the restaurant simulation
with configurable parameters.
"""

import argparse
import sys
import unittest
from pathlib import Path

from src.config import Config
from src.simulation import SimulationRunner

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def run_tests():
    """Run the test suite."""
    print("Running test suite...")
    loader = unittest.TestLoader()
    start_dir = "tests"
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print(
            f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)"
        )
        return False


def run_simulation(args):
    """Run the restaurant simulation with specified parameters."""
    # Create configuration
    config = Config()

    # Override config with command line arguments
    if args.duration:
        config.sim_duration = args.duration
    if args.arrival_rate:
        config.interarrival_time = args.arrival_rate
    if args.kitchen_servers:
        config.kitchen_servers = args.kitchen_servers
    if args.counter_servers:
        config.counter_servers = args.counter_servers
    if args.runs:
        config.num_runs = args.runs

    # Create and run simulation
    runner = SimulationRunner(config)

    if args.runs and args.runs > 1:
        # Run multiple simulations
        runner.run_multiple_simulations(args.runs, verbose=True)
    else:
        # Run single simulation
        runner.run_simulation(args.duration, verbose=True)


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Restaurant Simulation - A SimPy-based fast-food restaurant simulator"
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test command
    subparsers.add_parser("test", help="Run the test suite")

    # Simulation command
    sim_parser = subparsers.add_parser("simulate", help="Run the restaurant simulation")
    sim_parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=480,
        help="Simulation duration in minutes (default: 480)",
    )
    sim_parser.add_argument(
        "--arrival-rate",
        "-a",
        type=float,
        default=5.0,
        help="Average customer arrival interval in minutes (default: 5.0)",
    )
    sim_parser.add_argument(
        "--kitchen-servers",
        "-k",
        type=int,
        default=2,
        help="Number of kitchen servers (default: 2)",
    )
    sim_parser.add_argument(
        "--counter-servers",
        "-c",
        type=int,
        default=1,
        help="Number of counter servers (default: 1)",
    )
    sim_parser.add_argument(
        "--runs",
        "-r",
        type=int,
        default=1,
        help="Number of simulation runs (default: 1)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "test":
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.command == "simulate":
        run_simulation(args)
    else:
        # Default behavior - run a single simulation
        print("Restaurant Simulation")
        print("=" * 50)
        print("Use 'python main.py simulate --help' for options")
        print("Use 'python main.py test' to run tests")
        print()

        # Run default simulation
        config = Config()
        runner = SimulationRunner(config)
        runner.run_simulation(verbose=True)


if __name__ == "__main__":
    main()
