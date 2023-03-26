from typing import Optional
import random
import simpy
from src.config import Config

class Customer:
    """
    A class representing a customer in a restaurant simulation.

    Attributes:
        env (simpy.Environment): The simulation environment.
        id (int): The unique identifier for the customer.
        restaurant (MockRestaurant): The restaurant the customer is visiting.
        arrival_time (float): The time the customer arrived at the restaurant.
        order_time (Optional[float]): The time the customer placed their order.
        cook_time (Optional[float]): The time the customer's food started being cooked.
        service_time (Optional[float]): The time the customer received their food.
        config (Config): The configuration object for the simulation.
    """

    def __init__(self, env: simpy.Environment, id: int, restaurant: 'MockRestaurant', 
                 arrival_time: float, config: Config):
        self.env = env
        self.id = id
        self.restaurant = restaurant
        self.arrival_time = arrival_time
        self.order_time: Optional[float] = None
        self.cook_time: Optional[float] = None
        self.service_time: Optional[float] = None
        self.config = config
    
    def place_order(self) -> simpy.events.Event:
        """
        Places an order with the restaurant's order taker.
        """
        order_taker = self.restaurant.order_taker
        with order_taker.request() as req:
            yield req
            self.order_time = self.env.now
            yield self.env.timeout(random.uniform(self.config.mean_order_time-2, self.config.mean_order_time+2))

    def wait_for_food(self) -> simpy.events.Event:
        """
        Waits for the cook to prepare the customer's food.
        """
        cook = self.restaurant.cook
        with cook.request() as req:
            yield req
            self.cook_time = self.env.now
            yield self.env.timeout(random.uniform(self.config.mean_cook_time-3, self.config.mean_cook_time+3))

    def receive_food(self) -> simpy.events.Event:
        """
        Receives the customer's food from the server.
        """
        server = self.restaurant.server
        with server.request() as req:
            yield req
            self.service_time = self.env.now
            yield self.env.timeout(random.uniform(self.config.mean_service_time-1, self.config.mean_service_time+1))

    def leave(self) -> None:
        """
        Leaves the restaurant and adds the customer to the restaurant's metrics.
        """
        self.restaurant.metrics.add_customer(self)
