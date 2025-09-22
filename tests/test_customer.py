import unittest

from simpy import Environment

from src.config import Config
from src.customer import FoodAppCustomer, InHouseCustomer
from src.driver import Driver
from src.restaurant import Restaurant


class TestInHouseCustomer(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.config = Config()
        self.restaurant = Restaurant(self.env, self.config)
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


class TestFoodAppCustomer(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.config = Config()
        self.restaurant = Restaurant(self.env, self.config)
        self.driver = Driver(self.env, self.config)
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
