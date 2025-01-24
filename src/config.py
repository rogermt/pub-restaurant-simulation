from typing import Any, Dict, List


class Config:
    """
    Configuration settings for the fast food restaurant simulation.

    Attributes:
        interarrival_time (int): The average interarrival time for customers.
        kitchen_service_time (int): The average service time for customers at the kitchen station.
        counter_service_time (int): The average service time for customers at the counter station.
        kitchen_servers (int): The number of servers at the kitchen station.
        counter_servers (int): The number of servers at the counter station.
        kitchen_queue_size (int): The maximum queue size at the kitchen station.
        counter_queue_size (int): The maximum queue size at the counter station.
        warm_up_time (int): The warm-up time for the simulation.
        sim_duration (int): The duration of the simulation.
        num_runs (int): The number of simulation runs to perform.
        kitchen_wait_times (List[int]): List of kitchen wait times for each simulation run.
        kitchen_queue_lengths (List[int]): List of kitchen queue lengths for each simulation run.
        counter_wait_times (List[int]): List of counter wait times for each simulation run.
        counter_queue_lengths (List[int]): List of counter queue lengths for each simulation run.
        mean_order_time (float): The average time it takes a customer to place an order.
        mean_cook_time (float): The average time it takes to cook a customer's food.
        mean_serve_time (float): The average time it takes to serve a customer's food.
        driver_capacity (int): The number of external drivers available.
    """

    # Interarrival time for customers
    interarrival_time: int = 5

    # Mean service times for each station (in minutes)
    kitchen_service_time: int = 3
    counter_service_time: int = 1

    # Number of servers at each station
    kitchen_servers: int = 2
    counter_servers: int = 1

    # Maximum queue size for each station
    kitchen_queue_size: int = 5
    counter_queue_size: int = 3

    # Simulation run metrics
    warm_up_time: int = 60
    sim_duration: int = 480
    num_runs: int = 50

    # Placeholders to track wait times and queue lengths
    kitchen_wait_times: List[float] = []
    kitchen_queue_lengths: List[int] = []
    counter_wait_times: List[float] = []
    counter_queue_lengths: List[int] = []

    # Mean times for each step of customer service
    mean_order_time: float = 2
    mean_cook_time: float = 5
    mean_service_time: float = 4

    # Number of external drivers available
    driver_capacity: int = 10  # Adjust as needed

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Returns the configuration values as a dictionary.
        """
        return {
            "interarrival_time": cls.interarrival_time,
            "kitchen_service_time": cls.kitchen_service_time,
            "counter_service_time": cls.counter_service_time,
            "kitchen_servers": cls.kitchen_servers,
            "counter_servers": cls.counter_servers,
            "kitchen_queue_size": cls.kitchen_queue_size,
            "counter_queue_size": cls.counter_queue_size,
            "warm_up_time": cls.warm_up_time,
            "sim_duration": cls.sim_duration,
            "num_runs": cls.num_runs,
            "mean_order_time": cls.mean_order_time,
            "mean_cook_time": cls.mean_cook_time,
            "mean_service_time": cls.mean_service_time,
            "driver_capacity": cls.driver_capacity,
        }
