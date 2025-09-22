"""
Restaurant simulation runner with customer generation and metrics reporting.
"""
import random
import simpy
from typing import Generator, List, Tuple

from .config import Config
from .customer import FoodAppCustomer, InHouseCustomer
from .driver import Driver
from .restaurant import Restaurant


class SimulationConfig:
    """Configuration class for simulation parameters."""
    
    def __init__(self, duration: int = 480, interarrival_time: float = 5.0, 
                 kitchen_servers: int = 2, counter_servers: int = 1, num_runs: int = 1,
                 driver_capacity: int = 10):
        self.duration = duration
        self.sim_duration = duration  # Alias for compatibility
        self.interarrival_time = interarrival_time
        self.kitchen_servers = kitchen_servers
        self.counter_servers = counter_servers
        self.num_runs = num_runs
        self.driver_capacity = driver_capacity
        
        # Additional attributes for compatibility with existing code
        self.kitchen_service_time = 3
        self.counter_service_time = 1
        self.mean_order_time = 2
        self.mean_cook_time = 5
        self.mean_service_time = 4


class SimulationRunner:
    """
    Main simulation runner that orchestrates the restaurant simulation.
    
    Handles customer arrival generation, simulation execution, and metrics collection.
    """
    
    def __init__(self, config: Config = None):
        """Initialize the simulation runner with configuration."""
        self.config = config or Config()
        self.restaurant = None
        self.env = None
        
    def customer_generator(self, env: simpy.Environment, restaurant: Restaurant, driver_pool: Driver) -> Generator:
        """
        Generate customers arriving at the restaurant over time.
        
        Creates both InHouseCustomer and FoodAppCustomer instances based on
        configured arrival patterns.
        """
        customer_id = 1
        
        while True:
            # Wait for next customer arrival
            interarrival_time = random.expovariate(1.0 / self.config.interarrival_time)
            yield env.timeout(interarrival_time)
            
            # Record arrival time
            arrival_time = env.now
            
            # Randomly choose customer type (70% in-house, 30% food app)
            if random.random() < 0.7:
                customer = InHouseCustomer(env, customer_id, restaurant, arrival_time, self.config)
            else:
                customer = FoodAppCustomer(env, customer_id, restaurant, arrival_time, self.config, driver_pool)
            
            # Start the customer journey process
            if isinstance(customer, InHouseCustomer):
                env.process(self._inhouse_customer_journey(customer))
            else:
                env.process(self._foodapp_customer_journey(customer))
            customer_id += 1
    
    def _inhouse_customer_journey(self, customer: InHouseCustomer) -> Generator:
        """Process the complete journey for an in-house customer."""
        try:
            yield customer.env.process(customer.place_order())
            yield customer.env.process(customer.wait_for_food())
            yield customer.env.process(customer.receive_food())
            customer.leave()
        except Exception as e:
            print(f"Error in customer {customer.id} journey: {e}")
    
    def _foodapp_customer_journey(self, customer: FoodAppCustomer) -> Generator:
        """Process the complete journey for a food app customer."""
        try:
            yield customer.env.process(customer.place_order())
            yield customer.env.process(customer.wait_for_food())
            # Schedule pickup after food is ready
            pickup_time = customer.env.now + 5  # 5 minute pickup delay
            yield customer.env.process(customer.schedule_pickup(pickup_time))
            customer.leave()
        except Exception as e:
            print(f"Error in customer {customer.id} journey: {e}")
    
    def run_simulation(self, duration: int = None, verbose: bool = False) -> Tuple[Restaurant, dict]:
        """
        Run a single simulation for the specified duration.
        
        Args:
            duration: Simulation duration in minutes (uses config default if None)
            verbose: Whether to print detailed simulation events
            
        Returns:
            Tuple of (Restaurant instance, metrics dictionary)
        """
        duration = duration or self.config.sim_duration
        
        # Create SimPy environment, restaurant, and driver pool
        env = simpy.Environment()
        restaurant = Restaurant(env, self.config)
        driver_pool = Driver(env, self.config)
        
        # Start customer generation process
        env.process(self.customer_generator(env, restaurant, driver_pool))
        
        if verbose:
            print(f"Starting simulation for {duration} minutes...")
            print(f"Restaurant capacity: {self.config.kitchen_servers} kitchen, {self.config.counter_servers} counter")
            print(f"Customer arrival rate: every {self.config.interarrival_time} minutes on average")
            print("-" * 60)
        
        # Run the simulation
        env.run(until=duration)
        
        # Collect metrics
        metrics = self._collect_metrics(restaurant, duration)
        
        if verbose:
            self._print_simulation_results(metrics)
        
        return restaurant, metrics
    
    def run_multiple_simulations(self, num_runs: int = None, verbose: bool = False) -> List[dict]:
        """
        Run multiple simulation runs and collect aggregate statistics.
        
        Args:
            num_runs: Number of simulation runs (uses config default if None)
            verbose: Whether to print progress and results
            
        Returns:
            List of metrics dictionaries from each run
        """
        num_runs = num_runs or self.config.num_runs
        all_metrics = []
        
        if verbose:
            print(f"Running {num_runs} simulation runs...")
            print("=" * 60)
        
        for run_num in range(1, num_runs + 1):
            if verbose and run_num % 10 == 0:
                print(f"Completed {run_num}/{num_runs} runs...")
            
            _, metrics = self.run_simulation(verbose=False)
            metrics['run_number'] = run_num
            all_metrics.append(metrics)
        
        if verbose:
            self._print_aggregate_results(all_metrics)
        
        return all_metrics
    
    def _collect_metrics(self, restaurant: Restaurant, duration: int) -> dict:
        """Collect simulation metrics from the restaurant."""
        metrics = restaurant.get_metrics_summary()
        
        # Add simulation-level metrics
        total_customers = metrics.get('total_customers', 0)
        metrics.update({
            'simulation_duration': duration,
            'total_customers_served': total_customers,
            'customers_per_hour': (total_customers / duration) * 60 if duration > 0 else 0,
            'kitchen_utilization': self._calculate_utilization(
                metrics.get('total_kitchen_time', 0), 
                duration, 
                self.config.kitchen_servers
            ),
            'counter_utilization': self._calculate_utilization(
                metrics.get('total_counter_time', 0), 
                duration, 
                self.config.counter_servers
            )
        })
        
        return metrics
    
    def _calculate_utilization(self, total_service_time: float, duration: int, num_servers: int) -> float:
        """Calculate resource utilization percentage."""
        if duration == 0 or num_servers == 0:
            return 0.0
        return min(100.0, (total_service_time / (duration * num_servers)) * 100)
    
    def _print_simulation_results(self, metrics: dict):
        """Print detailed results from a single simulation run."""
        print("\n" + "=" * 60)
        print("SIMULATION RESULTS")
        print("=" * 60)
        print(f"Duration: {metrics['simulation_duration']} minutes")
        print(f"Total customers served: {metrics['total_customers_served']}")
        print(f"Customers per hour: {metrics['customers_per_hour']:.1f}")
        print()
        print("WAIT TIMES:")
        print(f"  Average kitchen wait: {metrics.get('avg_kitchen_wait', 0):.2f} minutes")
        print(f"  Average counter wait: {metrics.get('avg_counter_wait', 0):.2f} minutes")
        print(f"  Average total wait: {metrics.get('avg_total_wait', 0):.2f} minutes")
        print()
        print("RESOURCE UTILIZATION:")
        print(f"  Kitchen: {metrics['kitchen_utilization']:.1f}%")
        print(f"  Counter: {metrics['counter_utilization']:.1f}%")
        print()
        print("CUSTOMER BREAKDOWN:")
        print(f"  In-house customers: {metrics.get('inhouse_customers', 0)}")
        print(f"  Food app customers: {metrics.get('foodapp_customers', 0)}")
        print("=" * 60)
    
    def _print_aggregate_results(self, all_metrics: List[dict]):
        """Print aggregate statistics from multiple simulation runs."""
        if not all_metrics:
            return
        
        # Calculate averages
        avg_customers = sum(m['total_customers_served'] for m in all_metrics) / len(all_metrics)
        avg_customers_per_hour = sum(m['customers_per_hour'] for m in all_metrics) / len(all_metrics)
        avg_kitchen_util = sum(m['kitchen_utilization'] for m in all_metrics) / len(all_metrics)
        avg_counter_util = sum(m['counter_utilization'] for m in all_metrics) / len(all_metrics)
        
        print("\n" + "=" * 60)
        print(f"AGGREGATE RESULTS ({len(all_metrics)} runs)")
        print("=" * 60)
        print(f"Average customers served: {avg_customers:.1f}")
        print(f"Average customers per hour: {avg_customers_per_hour:.1f}")
        print(f"Average kitchen utilization: {avg_kitchen_util:.1f}%")
        print(f"Average counter utilization: {avg_counter_util:.1f}%")
        print("=" * 60)