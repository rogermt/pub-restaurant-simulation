# Design README for Flowchart TD

## Overview
This flowchart TD illustrates the process flow of a fast-food restaurant in a UK public house food service, which caters to both in-house and online customers. The system involves a customer placing an order, which is then sent to the kitchen for preparation. Once the food is ready, it is served to the customer or delivered through a food delivery app. The flowchart also includes queues for managing the order, cook, serve, and app order requests.

## Flowchart Structure
The flowchart consists of two subgraphs - Flow and Queue.

### Flow
The Flow subgraph displays the process flow and the interactions between the entities involved, as follows:

1. In-House Customer and Food App Customer place an order.
2. Order Taker/Server takes the order and sends it to the kitchen.
3. Kitchen prepares the food and notifies the Server and the Food Delivery App driver.
4. Server serves the food to the customer.
5. Food Delivery App driver delivers the food to the customer.

### Queue
The Queue subgraph displays the queues for each request type and the order in which they are processed, as follows:

1. Order Queue manages the order requests on a first-in-first-out basis.
2. Cook Queue manages the cook requests based on priority.
3. Serve Queue manages the serve requests on a first-in-first-out basis.
4. App Order Queue manages the app order requests on a first-in-first-out basis.

Note that physical delivery to the customer is not simulated in this project.

## Usage
To use this flowchart TD, simply follow the arrows in the Flow subgraph to understand the order processing system. The Queue subgraph provides a visual representation of the queues for each request type.

## Conclusion
This flowchart TD provides a clear and concise overview of the order processing system of a food service establishment. It demonstrates the interactions between the entities involved and the queues for managing the order, cook, serve, and app order requests.
