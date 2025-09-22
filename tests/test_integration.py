import unittest
from simpy import Environment

from src.config import Config
from src.customer import FoodAppCustomer, InHouseCustomer
from src.driver import Driver
from src.restaurant import Restaurant


class TestRestaurantIntegration(unittest.TestCase):
    """Integration tests that validate realistic restaurant operations."""

    def setUp(self):
        self.env = Environment()
        self.config = Config()
        self.restaurant = Restaurant(self.env, self.config)

    def test_restaurant_resources_match_config(self):
        """Test that restaurant resources are created according to configuration."""
        # Verify resource capacities match config
        self.assertEqual(
            self.restaurant.order_taker.capacity, self.config.counter_servers
        )
        self.assertEqual(self.restaurant.cook.capacity, self.config.kitchen_servers)
        self.assertEqual(self.restaurant.server.capacity, self.config.counter_servers)

    def test_restaurant_metrics_tracking(self):
        """Test that restaurant properly tracks customer metrics."""
        # Initially no customers
        self.assertEqual(self.restaurant.metrics.get_customer_count(), 0)
        self.assertEqual(self.restaurant.get_metrics_summary()["total_customers"], 0)

        # Create and process a customer
        customer = InHouseCustomer(self.env, 1, self.restaurant, 0, self.config)

        def customer_journey():
            yield self.env.process(customer.place_order())
            yield self.env.process(customer.wait_for_food())
            yield self.env.process(customer.receive_food())
            customer.leave()

        self.env.process(customer_journey())
        self.env.run()

        # Verify metrics were updated
        self.assertEqual(self.restaurant.metrics.get_customer_count(), 1)
        self.assertEqual(self.restaurant.get_metrics_summary()["total_customers"], 1)
        self.assertGreater(
            self.restaurant.get_metrics_summary()["average_wait_time"], 0
        )

    def test_multiple_customers_resource_contention(self):
        """Test that multiple customers properly compete for restaurant resources."""
        customers = []

        def create_customer_journey(customer_id):
            customer = InHouseCustomer(
                self.env, customer_id, self.restaurant, self.env.now, self.config
            )
            customers.append(customer)

            yield self.env.process(customer.place_order())
            yield self.env.process(customer.wait_for_food())
            yield self.env.process(customer.receive_food())
            customer.leave()

        # Create multiple customers simultaneously
        for i in range(3):
            self.env.process(create_customer_journey(i + 1))

        self.env.run()

        # All customers should be served
        self.assertEqual(self.restaurant.metrics.get_customer_count(), 3)
        self.assertEqual(len(customers), 3)

        # Verify all customers have completion times
        for customer in customers:
            self.assertIsNotNone(customer.order_time)
            self.assertIsNotNone(customer.cook_time)
            self.assertIsNotNone(customer.service_time)

    def test_food_app_customer_integration(self):
        """Test that food app customers work properly with real restaurant and driver."""
        driver = Driver(self.env, self.config)
        customer = FoodAppCustomer(self.env, 1, self.restaurant, 0, self.config, driver)

        def food_app_journey():
            yield self.env.process(customer.place_order())
            yield self.env.process(customer.wait_for_food())
            pickup_time = self.env.now + 5
            yield self.env.process(customer.schedule_pickup(pickup_time))
            customer.leave()

        self.env.process(food_app_journey())
        self.env.run()

        # Verify customer was processed
        self.assertEqual(self.restaurant.metrics.get_customer_count(), 1)
        self.assertIsNotNone(customer.order_time)
        self.assertIsNotNone(customer.cook_time)
        self.assertIsNotNone(customer.pickup_time)

    def test_mixed_customer_types(self):
        """Test that in-house and food app customers can coexist."""
        driver = Driver(self.env, self.config)

        # Create both types of customers
        in_house_customer = InHouseCustomer(
            self.env, 1, self.restaurant, 0, self.config
        )
        food_app_customer = FoodAppCustomer(
            self.env, 2, self.restaurant, 0, self.config, driver
        )

        def in_house_journey():
            yield self.env.process(in_house_customer.place_order())
            yield self.env.process(in_house_customer.wait_for_food())
            yield self.env.process(in_house_customer.receive_food())
            in_house_customer.leave()

        def food_app_journey():
            yield self.env.process(food_app_customer.place_order())
            yield self.env.process(food_app_customer.wait_for_food())
            pickup_time = self.env.now + 3
            yield self.env.process(food_app_customer.schedule_pickup(pickup_time))
            food_app_customer.leave()

        # Start both journeys
        self.env.process(in_house_journey())
        self.env.process(food_app_journey())
        self.env.run()

        # Both customers should be served
        self.assertEqual(self.restaurant.metrics.get_customer_count(), 2)

    def test_restaurant_reset_functionality(self):
        """Test that restaurant metrics can be reset properly."""
        customer = InHouseCustomer(self.env, 1, self.restaurant, 0, self.config)

        def simple_journey():
            yield self.env.process(customer.place_order())
            customer.leave()

        self.env.process(simple_journey())
        self.env.run()

        # Verify customer was tracked
        self.assertEqual(self.restaurant.metrics.get_customer_count(), 1)

        # Reset and verify
        self.restaurant.reset_metrics()
        self.assertEqual(self.restaurant.metrics.get_customer_count(), 0)
        self.assertEqual(self.restaurant.get_metrics_summary()["total_customers"], 0)


if __name__ == "__main__":
    unittest.main()
