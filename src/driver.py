import simpy
from src.config import Config

class Driver(simpy.Resource):
    def __init__(self, env: simpy.Environment, config: Config):
        super().__init__(env, capacity=simpy.core.Infinity)
        self.config = config
