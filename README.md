# Pub Restaurant Simulation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This is a simulation of a fast-food restaurant in a UK pub, implemented using
the SimPy simulation library in Python. SimPy is a powerful discrete-event
simulation library that is well-suited for modeling and simulating complex
systems. Discrete event simulations are used to model systems where events occur
at discrete points in time, rather than continuously. In this simulation,
customer arrivals, order placement, food preparation, and order delivery are
modeled as discrete events. The simulation aims to optimize the restaurant's
performance by minimizing customer wait times and maximizing the number of
customers served.

The simulation comes with an easy-to-use command-line interface, a modular code
structure for easy customization and extension, a comprehensive test suite for
confident code changes, and a well-documented codebase.

## Requirements

- Python 3.x
- SimPy

## Installation

1. Clone the repository:
   `git clone https://github.com/rogermt/pub-restaurant-simulation.git`
1. Install the dependencies: `pip install -r requirements.txt`

## Usage

1. Navigate to the root directory of the project.
1. Run `python main.py` to start the simulation.

The simulation parameters can be modified by editing the `config.py` file.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

## License

This project is licensed under the terms of the MIT license. See
[LICENSE](LICENSE) for more information.
