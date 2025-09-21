import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator, Optional

import simpy

from src.config import Config
from src.driver import Driver

if TYPE_CHECKING:
    from src.restaurant import Restaurant  # Import from actual module when available
else:
    from src.restaurant_stub import Restaurant  # Import the stub class


class Customer(ABC):
    """
    Abstract base class representing a customer in a restaurant simulation.

    Attributes:
    -----------
    env : simpy.Environment
        The simulation environment.
    id : int
        The unique identifier for the customer.
    restaurant : MockRestaurant
        The restaurant the customer is ordering from.
    arrival_time : float
        The time the customer arrived at the restaurant.
    config : Config
        The configuration object for the simulation.

    Methods:
    --------
    place_order() Generator[simpy.events.Event, None, None]:
        Sends an order request to the restaurant's order taker.
    wait_for_food() Generator[simpy.events.Event, None, None]:
        Sends a request for food to the cook and waits for it to be prepared.
    leave() -> None:
        Records the customer's departure from the restaurant and adds them to the restaurant's metrics.
    """

    def __init__(
        self,
        env: simpy.Environment,
        id: int,
        restaurant: "Restaurant",
        arrival_time: float,
        config: Config,
    ):
        """
        Initializes a new instance of the Customer class.

        Parameters:
        -----------
        env : simpy.Environment
            The simulation environment.
        id : int
            The unique identifier for the customer.
        restaurant : MockRestaurant
            The restaurant the customer is ordering from.
        arrival_time : float
            The time the customer arrived at the restaurant.
        config : Config
            The configuration object for the simulation.
        """
        self.env = env
        self.id = id
        self.restaurant = restaurant
        self.arrival_time = arrival_time
        self.config = config

        self.order_time: Optional[float] = None
        self.cook_time: Optional[float] = None
        self.service_time: Optional[float] = None

    @abstractmethod
    def place_order(self) -> Generator[simpy.events.Event, None, None]:
        """
        Abstract method for placing an order with the restaurant's order taker.

        Returns:
        --------
        Generator[simpy.events.Event, None, None]:
            A SimPy event representing the order request.
        """
        pass

    @abstractmethod
    def wait_for_food(self) -> Generator[simpy.events.Event, None, None]:
        """
        Abstract method for sending a request for food to the cook and waiting for it to be prepared.

        Returns:
        --------
        simpy.events.Event:
            A SimPy event representing the food request.
        """
        pass

    @abstractmethod
    def leave(self) -> None:
        """
        Abstract method for recording the customer's departure from the restaurant and adding them to the restaurant's metrics.
        """
        pass


class InHouseCustomer(Customer):
    """
    Class representing a customer who will dine in at the restaurant.

    Attributes:
    -----------
    env : simpy.Environment
        The simulation environment.
    id : int
        The unique identifier for the customer.
    restaurant : MockRestaurant
        The restaurant the customer is ordering from.
    arrival_time : float
        The time the customer arrived at the restaurant.
    config : Config
        The configuration object for the simulation.
    order_time : Optional[float]
        The time the customer placed their order.
    cook_time : Optional[float]
        The time the cook started preparing the customer's food.
    service_time : Optional[float]
        The time the customer received their food.

    Methods:
    --------
    place_order() Generator[simpy.events.Event, None, None]
        Places an order with the restaurant's order taker.
    wait_for_food() Generator[simpy.events.Event, None, None]
        Waits for the cook to prepare the customer's food.
    receive_food() Generator[simpy.events.Event, None, None]
        Serves the food to the customer.
    leave() -> None
        Adds the customer to the restaurant's metrics.
    """

    def __init__(
        self,
        env: simpy.Environment,
        id: int,
        restaurant: "Restaurant",
        arrival_time: float,
        config: Config,
    ):
        super().__init__(env, id, restaurant, arrival_time, config)

    def place_order(self) -> Generator[simpy.events.Event, None, None]:
        """
        Places an order with the restaurant's order taker.

        Returns:
        --------
        order : Generator[simpy.events.Event, None, None]
            The event that gets triggered when the order is taken by the restaurant's order taker.
        """
        # Send an order request to the restaurant's order taker
        print("Sending order request to order taker...")
        order_taker = self.restaurant.order_taker
        with order_taker.request() as order:
            yield order

            # Record the time the order was placed
            print("Recording the time the order was placed...")
            self.order_time = self.env.now

            # Wait for the order to be taken
            print("Waiting for the order to be taken...")
            yield self.env.timeout(
                random.uniform(
                    self.config.mean_order_time - 2, self.config.mean_order_time + 2
                )
            )



    def wait_for_food(self) -> Generator[simpy.events.Event, None, None]:
        """
        Waits for the cook to prepare the customer's food.

        Returns:
        --------
        food : Generator[simpy.events.Event, None, None]
            The event that gets triggered when the cook finishes preparing the customer's food.
        """
        # Send a request for food to the cook
        cook = self.restaurant.cook
        with cook.request() as food:
            yield food

            # Record the time the cook started cooking the customer's food
            self.cook_time = self.env.now

            # Wait for the cook to prepare the food
            yield self.env.timeout(
                random.uniform(
                    self.config.mean_cook_time - 2, self.config.mean_cook_time + 2
                )
            )


    def receive_food(self) -> Generator[simpy.events.Event, None, None]:
        """
        Serves the food to the customer.

        Returns:
        --------
        serve : Generator[simpy.events.Event, None, None]
            The event that gets triggered when the customer is served their food.
        """
        server = self.restaurant.server
        with server.request() as req:
            yield req

            # Serve the food to the customer
            yield self.env.timeout(
                random.uniform(
                    self.config.mean_service_time - 2, self.config.mean_service_time + 2
                )
            )

            # Record the time the customer received their food
            self.service_time = self.env.now

    def leave(self) -> None:
        """
        Adds the customer to the restaurant's metrics.
        """
        # Add the customer to the restaurant's metrics
        self.restaurant.metrics.add_customer(self)


class FoodAppCustomer(Customer):
    """
    Represents a customer who orders food from a restaurant through a food app and schedules a pickup time by the food app driver.

    Attributes:
        env (simpy.Environment): The simulation environment.
        id (int): The unique identifier for the customer.
        restaurant (MockRestaurant): The restaurant from which the customer is ordering.
        arrival_time (float): The time at which the customer arrives at the restaurant.
        config (Config): The configuration object for the simulation.
        pickup_time (Optional[float]): The scheduled time for the driver to pick up their food.

    Methods:
        place_order(): Sends an order request direct to the cook.
        wait_for_food(): Sends a request for food to the kitchen and waits for the food to be prepared.
        schedule_pickup(pickup_time: float): Schedules a pickup event for when the food is ready.
        leave(): Adds the customer to the restaurant's metrics.
    """

    def __init__(
        self,
        env: simpy.Environment,
        id: int,
        restaurant: "Restaurant",
        arrival_time: float,
        config: Config,
        driver: Driver,
    ):
        """
        Initializes a new instance of the FoodAppCustomer class.

        Args:
            env (simpy.Environment): The simulation environment.
            id (int): The unique identifier for the customer.
            restaurant (MockRestaurant): The restaurant from which the customer is ordering.
            arrival_time (float): The time at which the driver arrives at the restaurant.
            config (Config): The configuration object for the simulation.
            driver (Driver): The driver from the Food App Delivery
        """
        super().__init__(env, id, restaurant, arrival_time, config)
        self.driver = driver
        self.pickup_time: Optional[float] = None

    def place_order(self):
        """
        Sends an order request to the kitchen cook.
        """
        cook = self.restaurant.cook
        with cook.request() as order:
            yield order

            # Record the time the order was placed
            self.order_time = self.env.now

            # Wait for the order to be taken
            yield self.env.timeout(
                random.uniform(
                    self.config.mean_order_time - 2, self.config.mean_order_time + 2
                )
            )


    def wait_for_food(self):
        """
        Sends a request for food to the kitchen and waits for the food to be prepared.
        """
        # Send a request for food to the cook
        cook = self.restaurant.cook
        with cook.request() as food:
            yield food

            # Record the time the cook started cooking the customer's food
            self.cook_time = self.env.now

            # Wait for the cook to prepare the food
            yield self.env.timeout(
                random.uniform(
                    self.config.mean_cook_time - 2, self.config.mean_cook_time + 2
                )
            )


    def schedule_pickup(self, pickup_time: float):
        self.pickup_time = pickup_time

        while self.env.now < self.cook_time:
            yield self.env.timeout(1)

        with self.driver.request() as req:  # "with" handles release automatically
            yield req
            wait_time = max(pickup_time - self.env.now, 0)
            yield self.env.timeout(wait_time)

    def leave(self):
        """
        Adds the customer to the restaurant's metrics.
        """
        self.restaurant.metrics.add_customer(self)
