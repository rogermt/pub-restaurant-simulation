import random

class Customer:
    """
    A class representing a customer in a restaurant simulation.

    Attributes:
        env (simpy.Environment): The simulation environment.
        id (int): The unique identifier for the customer.
        restaurant (MockRestaurant): The restaurant the customer is visiting.
        arrival_time (float): The time the customer arrived at the restaurant.
        order_time (float): The time the customer placed their order.
        cook_time (float): The time the customer's food started being cooked.
        service_time (float): The time the customer received their food.
    """

    def __init__(self, env, id, restaurant, arrival_time):
        self.env = env
        self.id = id
        self.restaurant = restaurant
        self.arrival_time = arrival_time
        self.order_time = None
        self.cook_time = None
        self.service_time = None
    
    def place_order(self):
        """
        Places an order with the restaurant's order taker.
        """
        order_taker = self.restaurant.order_taker
        with order_taker.request() as req:
            yield req
            self.order_time = self.env.now
            yield self.env.timeout(random.uniform(self.restaurant.mean_order_time-2, self.restaurant.mean_order_time+2))

    def wait_for_food(self):
        """
        Waits for the cook to prepare the customer's food.
        """
        cook = self.restaurant.cook
        with cook.request() as req:
            yield req
            self.cook_time = self.env.now
            yield self.env.timeout(random.uniform(self.restaurant.mean_cook_time-3, self.restaurant.mean_cook_time+3))

    def receive_food(self):
        """
        Receives the customer's food from the server.
        """
        server = self.restaurant.server
        with server.request() as req:
            yield req
            self.service_time = self.env.now
            yield self.env.timeout(random.uniform(self.restaurant.mean_serve_time-1, self.restaurant.mean_serve_time+1))

    def leave(self):
        """
        Leaves the restaurant and adds the customer to the restaurant's metrics.
        """
        self.restaurant.metrics.add_customer(self)
