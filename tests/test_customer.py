import simpy
import unittest

from typing import Any, List
from src.customer import Customer
from src.config import Config


class MockOrderTaker(simpy.Resource):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    
class MockRestaurant:
    def __init__(self, mean_order_time: float, mean_cook_time: float, mean_serve_time: float) -> None:
        self.mean_order_time: float = mean_order_time
        self.mean_cook_time: float = mean_cook_time
        self.mean_serve_time: float = mean_serve_time


class MockCook(simpy.Resource):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        

class MockServer(simpy.Resource):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

class MockMetrics:
    def __init__(self):
        self.customers: List = []

    def add_customer(self, customer):
        self.customers.append(customer)

    def reset(self):
        self.customers = []
        

class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        
        mean_order_time = 5
        mean_cook_time = 5
        mean_serve_time = 5
        self.restaurant = MockRestaurant(mean_order_time, mean_cook_time, mean_serve_time)
        
        self.restaurant.order_taker = MockOrderTaker(self.env,3)  
        self.restaurant.cook = MockCook(self.env, 3)
        self.restaurant.server = MockServer(self.env, 3)

        self.metrics = MockMetrics()
        self.restaurant.metrics = self.metrics
        config = Config()
        self.customer = Customer(self.env, 1, self.restaurant, 0, config)


    def test_place_order(self):
        self.env.process(self.customer.place_order())
        self.assertTrue(self.customer.order_time is None)
        self.env.run()
        self.assertIsNotNone(self.customer.order_time)
        self.assertTrue(self.customer.order_time >= 0)
        self.assertTrue(self.customer.order_time >= self.customer.arrival_time)

        
    def test_wait_for_food(self):
        self.env.process(self.customer.wait_for_food())
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
        

    def test_leavetest_leave(self):
        self.customer.leave()
        self.assertTrue(len(self.metrics.customers) == 1)

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
        

if __name__ == '__main__':
    unittest.main()
