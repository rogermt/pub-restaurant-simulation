import unittest
from simpy import Environment, Resource
from typing import Any, List
from src.config import Config
from src.customer import InHouseCustomer

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
    def __init__(self, env: Environment, mean_order_time: float, mean_cook_time: float, mean_service_time: float, order_taker: Resource, cook: Resource, server: Resource, metrics: "MockMetrics" ) -> None:
        self.env = env
        self.mean_order_time: float = mean_order_time
        self.mean_cook_time: float = mean_cook_time
        self.mean_service_time: float = mean_service_time
        self.order_taker = order_taker  
        self.cook = cook
        self.server = server
        self.metrics = metrics


class TestInHouseCustomer(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        mean_order_time = 5
        mean_cook_time = 5
        mean_service_time = 5
        self.restaurant = MockRestaurant(self.env, mean_order_time, mean_cook_time, mean_service_time, MockOrderTaker(self.env,3), MockCook(self.env, 3), MockServer(self.env, 3), MockMetrics())
        self.metrics = MockMetrics()
        self.config = Config()

        self.customer = InHouseCustomer(self.env, 1, self.restaurant, 0, self.config)

    def test_place_order(self):
        # create a customer instance
        customer = self.customer

        #customer place order
        self.env.process(customer.place_order())
        self.assertTrue(customer.order_time is None)
        self.env.run()

        #ensuring that the order was placed after the customer's arrival.
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
        
    