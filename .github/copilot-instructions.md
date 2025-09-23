# Copilot Instructions for pub-restaurant-simulation

## Project Overview

- This project simulates a fast-food restaurant in a UK pub using SimPy
  (discrete-event simulation in Python).
- The simulation models both in-house and food app (delivery) customers, order
  processing, kitchen/counter resources, and delivery drivers.
- The codebase is modular: key components are in `src/` (see below), with tests
  in `tests/` and documentation in `docs/`.

## Key Components

- `main.py`: CLI entry point. Supports running the simulation and test suite.
  Accepts command-line arguments to override config.
- `src/config.py`: Central configuration for simulation parameters (e.g.,
  interarrival times, server counts, queue sizes). Most parameters can be
  overridden via CLI.
- `src/simulation.py`: Simulation runner. Handles environment setup, customer
  generation, and metrics reporting.
- `src/restaurant.py`: Defines the restaurant, its resources (order taker, cook,
  server), and metrics tracking.
- `src/customer.py`: Abstract base class and concrete classes for in-house and
  food app customers. Encapsulates customer journey logic.
- `src/driver.py`: Models delivery drivers as SimPy resources.

## Developer Workflows

- **Run simulation:** `python main.py` (add `--help` for CLI options)
- **Run all tests:** `python main.py --test` or `pytest`
- **Modify config:** Edit `src/config.py` or use CLI args (see `main.py` for
  mapping)
- **Add features:** Extend or subclass components in `src/`. Follow the modular,
  class-based structure.

## Project Conventions

- All simulation logic is encapsulated in classes; avoid global state.
- Use SimPy's `Environment` and `Resource` for all event-driven logic.
- Metrics are tracked via the `Metrics` class in `restaurant.py` and reported at
  the end of each run.
- Customer types are extensible; see `customer.py` for base/derived patterns.
- Tests use `unittest` and are located in `tests/`. Integration tests validate
  realistic multi-component flows.

## Integration Points & Patterns

- **SimPy** is the core simulation engine; all time/event logic should use it.
- **Config** is passed to all major components for consistency.
- **Restaurant** manages all resources and metrics; customers interact with it
  for all actions.
- **Drivers** are modeled as a SimPy resource for food app deliveries.

## Examples

- To add a new customer type, subclass `Customer` in `customer.py` and update
  the simulation runner.
- To change queueing logic, modify the relevant resource or queue in
  `restaurant.py`.

## References

- See `README.md` for high-level overview and setup.
- See `docs/README.md` and `simulation_flowchart.png` for process flow and
  architecture.

______________________________________________________________________

For any new AI agent, follow these conventions and reference the above files for
patterns. When in doubt, prefer class-based, modular, and testable code.
