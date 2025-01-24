import unittest
from typing import Any, List

from simpy import Environment, Resource

from src.config import Config
from src.customer import FoodAppCustomer, InHouseCustomer
from src.driver import Driver


class MockOrderTaker(Resource):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class MockCook(Resource):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class MockServer(Resource):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class MockMetrics:
    def __init__(self):
        self.customers: List = []

    def add_customer(self, customer):
        self.customers.append(customer)

    def reset(self):
        self.customers = []


class MockRestaurant:
    def __init__(
        self,
        env: Environment,
        mean_order_time: float,
        mean_cook_time: float,
        mean_service_time: float,
        order_taker: Resource,
        cook: Resource,
        server: Resource,
        metrics: "MockMetrics",
    ) -> None:
        self.env = env
        self.mean_order_time: float = mean_order_time
        self.mean_cook_time: float = mean_cook_time
        self.mean_service_time: float = mean_service_time
        self.order_taker = order_taker
        self.cook = cook
        self.server = server
        self.metrics = metrics

    def notify_driver_arrival(self):
        pass


class MockDriver(Driver):
    def __init__(self, env: Environment) -> None:
        super().__init__(env, Config())  # Pass required arguments for Driver


class TestInHouseCustomer(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        mean_order_time = 5
        mean_cook_time = 5
        mean_service_time = 5
        self.restaurant = MockRestaurant(
            self.env,
            mean_order_time,
            mean_cook_time,
            mean_service_time,
            MockOrderTaker(self.env, 3),
            MockCook(self.env, 3),
            MockServer(self.env, 3),
            MockMetrics(),
        )
        self.metrics = MockMetrics()
        self.config = Config()

        self.customer = InHouseCustomer(self.env, 1, self.restaurant, 0, self.config)

    def test_place_order(self):
        # create a customer instance
        customer = self.customer

        # customer place order
        self.env.process(customer.place_order())
        self.assertTrue(customer.order_time is None)
        self.env.run()

        # ensuring that the order was placed after the customer's arrival.
        self.assertIsNotNone(customer.order_time)
        self.assertTrue(customer.order_time >= 0)
        self.assertTrue(customer.order_time >= customer.arrival_time)

    def test_wait_for_food(self):
        self.env.process(self.customer.wait_for_food())
        self.assertTrue(self.customer.cook_time is None)
        self.env.run()
        self.assertIsNotNone(self.customer.cook_time)
        self.assertTrue(self.customer.cook_time >= 0)
        self.assertTrue(self.customer.cook_time >= self.customer.arrival_time)

    def test_receive_food(self):
        self.env.process(self.customer.receive_food())
        self.env.run()
        self.assertIsNotNone(self.customer.service_time)
        self.assertTrue(self.customer.service_time >= 0)
        self.assertTrue(self.customer.service_time >= self.customer.arrival_time)

    def test_leave(self):
        self.customer.leave()
        self.assertTrue(len(self.restaurant.metrics.customers) == 1)

    def test_place_order_with_request(self):
        self.env.process(self.customer.place_order())
        self.assertTrue(self.customer.order_time is None)
        self.env.run()
        self.assertIsNotNone(self.customer.order_time)
        self.assertTrue(self.customer.order_time >= 0)
        self.assertTrue(self.customer.order_time >= self.customer.arrival_time)

    def test_wait_for_food_with_request(self):
        self.env.process(self.customer.place_order())
        self.env.process(self.customer.wait_for_food())
        self.env.run()
        self.assertIsNotNone(self.customer.cook_time)
        self.assertTrue(self.customer.cook_time >= 0)
        self.assertTrue(self.customer.cook_time >= self.customer.order_time)

    def test_receive_food_with_request(self):
        self.env.process(self.customer.place_order())
        self.env.process(self.customer.wait_for_food())
        self.env.process(self.customer.receive_food())
        self.env.run()
        self.assertIsNotNone(self.customer.service_time)
        self.assertTrue(self.customer.service_time >= 0)
        self.assertTrue(self.customer.service_time >= self.customer.order_time)


class TestFoodAppCustomer(unittest.TestCase):

    def setUp(self):
        self.env = Environment()
        mean_order_time = 5
        mean_cook_time = 5
        mean_service_time = 5
        self.restaurant = MockRestaurant(
            self.env,
            mean_order_time,
            mean_cook_time,
            mean_service_time,
            MockOrderTaker(self.env, 3),
            MockCook(self.env, 3),
            MockServer(self.env, 3),
            MockMetrics(),
        )
        self.config = Config()
        self.metrics = MockMetrics()
        self.driver = MockDriver(self.env)

        self.customer = FoodAppCustomer(
            self.env, 1, self.restaurant, 0, self.config, self.driver
        )

    def test_place_order(self):
        # create a customer instance
        customer = self.customer
        # customer place order
        self.env.process(customer.place_order())
        self.assertTrue(customer.order_time is None)

        self.env.run()

        self.assertIsNotNone(customer.order_time)
        self.assertTrue(customer.order_time >= 0)
        self.assertTrue(customer.order_time >= customer.arrival_time)

    def test_wait_for_food(self):
        # create a customer instance
        customer = self.customer

        # customer place order
        self.env.process(customer.place_order())
        self.env.run()

        # customer wait for food
        self.env.process(customer.wait_for_food())

        self.assertTrue(customer.cook_time is None)

        self.env.run()

        self.assertIsNotNone(customer.cook_time)
        self.assertTrue(customer.cook_time >= customer.order_time)

    def test_schedule_pickup(self):
        # create a customer instance
        customer = self.customer

        # customer place order and wait for food
        self.env.process(customer.place_order())
        self.env.process(customer.wait_for_food())
        self.env.run()

        # customer schedules a pickup time
        pickup_time = 20
        self.env.process(customer.schedule_pickup(pickup_time))

        self.assertTrue(customer.pickup_time is None)

        self.env.run()

        self.assertIsNotNone(customer.pickup_time)
        self.assertTrue(customer.pickup_time >= customer.cook_time)
        self.assertTrue(customer.pickup_time == pickup_time)

    def test_leave(self):
        # create a customer instance
        customer = self.customer

        # customer place order, wait for food, schedule pickup, and leave
        self.env.process(customer.place_order())
        self.env.process(customer.wait_for_food())
        self.env.run()

        pickup_time = 20
        self.env.process(customer.schedule_pickup(pickup_time))
        self.env.run()

        customer.leave()

        self.assertEqual(len(self.restaurant.metrics.customers), 1)
        self.assertEqual(self.restaurant.metrics.customers[0].id, customer.id)
