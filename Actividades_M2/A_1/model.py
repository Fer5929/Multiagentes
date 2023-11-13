import random
from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa import DataCollector
from agent import RandomAgent, ObstacleAgent, DirtyAgent, ChargerAgent

class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, N, width, height, T, initial_num_dirty):
        self.num_agents = N
        self.initial_num_dirty = initial_num_dirty
        # Multigrid is a special type of grid where each cell can contain multiple agents.
        self.grid = MultiGrid(width,height,torus = False) 

        # RandomActivation is a scheduler that activates each agent once per step, in random order.
        self.schedule = RandomActivation(self)
        
        self.running = True 

        self.datacollector = DataCollector( 
            agent_reporters={"Steps": lambda a: a.steps_taken if isinstance(a, RandomAgent) else 0},
        )

        self.T = T
        self.time=T

        # Function to generate random positions
        pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
        #list with all the boarder positions
        border = [(0,i) for i in range(width)] + [(width-1,i) for i in range(width)] + [(i,0) for i in range(height)] + [(i,height-1) for i in range(height)]
        #add agents to random empty boarder cells
        for i in range(N):
            agent = RandomAgent(i, self)
            self.schedule.add(agent)
            pos = border[i]
            while not self.grid.is_cell_empty(pos):
                pos = border[i]
            self.grid.place_agent(agent, pos)

        
       
        # Add obstacles to random empty grid cells
        for i in range(20):
            obs = ObstacleAgent(i + 2000, self)
            self.schedule.add(obs)
            pos = pos_gen(self.grid.width, self.grid.height)
            while not self.grid.is_cell_empty(pos):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(obs, pos)

        # Add dirty cells to random empty grid cells
        for i in range(initial_num_dirty):
            dirty = DirtyAgent(i + 3000, self)  # Adjust the unique_id range
            self.schedule.add(dirty)
            pos = pos_gen(self.grid.width, self.grid.height)
            while not self.grid.is_cell_empty(pos):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(dirty, pos)
        
        # Add Charger to same cells as RandomAgents
        for agent in self.schedule.agents:
            if isinstance(agent, RandomAgent):
                charger = ChargerAgent(agent.unique_id + 4000, self)
                self.schedule.add(charger)
                self.grid.place_agent(charger, agent.pos)

        
        self.datacollector.collect(self)

    def step(self):
        # Check stopping conditions
        if self.time <= 0 or not any(isinstance(agent, DirtyAgent) for agent in self.schedule.agents):
            self.running = False
            return
        print(f"Time remaining: {self.time}")  # Print T on the screen
        self.schedule.step()
        self.datacollector.collect(self)
        self.time -= 1

    