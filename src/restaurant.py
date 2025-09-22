from typing import List
import simpy
from src.config import Config


class Metrics:
    """
    Tracks customer metrics and performance data for the restaurant simulation.
    
    Attributes:
        customers (List): List of customers who have completed their journey
    """
    
    def __init__(self):
        self.customers: List = []
    
    def add_customer(self, customer) -> None:
        """
        Add a customer to the metrics tracking.
        
        Args:
            customer: The customer object to track
        """
        self.customers.append(customer)
    
    def reset(self) -> None:
        """Reset all metrics data."""
        self.customers = []
    
    def get_customer_count(self) -> int:
        """Get the total number of customers served."""
        return len(self.customers)
    
    def get_average_wait_time(self) -> float:
        """Calculate average wait time for all customers."""
        if not self.customers:
            return 0.0
        
        total_wait_time = 0.0
        count = 0
        
        for customer in self.customers:
            if hasattr(customer, 'service_time') and hasattr(customer, 'arrival_time'):
                if customer.service_time is not None and customer.arrival_time is not None:
                    total_wait_time += customer.service_time - customer.arrival_time
                    count += 1
        
        return total_wait_time / count if count > 0 else 0.0


class Restaurant:
    """
    Core restaurant class that manages all restaurant operations and resources.
    
    This class coordinates the restaurant's staff (order takers, cooks, servers),
    tracks metrics, and provides the main interface for customer interactions.
    
    Attributes:
        env (simpy.Environment): The simulation environment
        config (Config): Configuration settings for the restaurant
        order_taker (simpy.Resource): Resource representing order taking staff
        cook (simpy.Resource): Resource representing kitchen/cooking staff  
        server (simpy.Resource): Resource representing serving staff
        metrics (Metrics): Object to track customer and performance metrics
    """
    
    def __init__(self, env: simpy.Environment, config: Config):
        """
        Initialize the restaurant with staff resources and metrics tracking.
        
        Args:
            env (simpy.Environment): The simulation environment
            config (Config): Configuration object with restaurant settings
        """
        self.env = env
        self.config = config
        
        # Initialize staff resources based on configuration
        self.order_taker = simpy.Resource(env, capacity=config.counter_servers)
        self.cook = simpy.Resource(env, capacity=config.kitchen_servers) 
        self.server = simpy.Resource(env, capacity=config.counter_servers)
        
        # Initialize metrics tracking
        self.metrics = Metrics()
    
    def notify_driver_arrival(self) -> None:
        """
        Handle notification when a delivery driver arrives.
        
        This method can be extended to implement driver arrival logic,
        such as updating metrics or triggering events.
        """
        # Placeholder for driver arrival handling
        pass
    
    def reset_metrics(self) -> None:
        """Reset all restaurant metrics."""
        self.metrics.reset()
    
    def get_metrics_summary(self) -> dict:
        """
        Get a summary of restaurant performance metrics.
        
        Returns:
            dict: Dictionary containing key performance metrics
        """
        return {
            'total_customers': self.metrics.get_customer_count(),
            'average_wait_time': self.metrics.get_average_wait_time(),
        }