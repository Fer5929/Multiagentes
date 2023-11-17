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
            agent_reporters={"Steps": lambda a: a.steps if isinstance(a, RandomAgent) else 0}, #cuenta los pasos dados por cada agente
            model_reporters={"Trash": lambda m: sum(1 for agent in m.schedule.agents if isinstance(agent, DirtyAgent))} #lleva cuenta de la basura en el modelo
        )
        
        #tiempo de simulacion
        self.T = T
        self.time = T

        # Function to generate random positions
        pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
        #list with all the boarder positions
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]
        
        #Agente en  (1,1)
        agent = RandomAgent(0, self)
        self.schedule.add(agent)
        pos = (1,1)
        while not self.grid.is_cell_empty(pos):
            pos = (1,1)
        agent.set_initial_position(pos)
        self.grid.place_agent(agent, pos)
        

        
       
        # Agrega los obstaculos a posiciones random vacias
        for i in range(20):
            obs = ObstacleAgent(i + 2000, self)
            self.schedule.add(obs)
            pos = pos_gen(self.grid.width, self.grid.height)
            while not self.grid.is_cell_empty(pos) or self.is_agent_nearby(pos):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(obs, pos)

        # Lo mismo que para los obstaculos pero para la basura
        for i in range(10):
            dirty = DirtyAgent(i + 3000, self)  
            self.schedule.add(dirty)
            pos = pos_gen(self.grid.width, self.grid.height)
            while not self.grid.is_cell_empty(pos):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(dirty, pos)
        
        # Agrega la misma cantidad de RandomAgents que de ChargerAgents pero los coloca en la posición inicial de cada RandomAgent
        for agent in self.schedule.agents:
            if isinstance(agent, RandomAgent):
                charger = ChargerAgent(agent.unique_id + 4000, self)
                self.schedule.add(charger)
                self.grid.place_agent(charger, agent.pos)

        
        self.datacollector.collect(self)

    def step(self):
        # La simulación termina si se acaba el tiempo o si no hay agentes sucios
        if self.time <= 0 or not any(isinstance(agent, DirtyAgent) for agent in self.schedule.agents):
            self.running = False
            return
        print(f"Time remaining: {self.time}")  
        self.schedule.step()
        self.datacollector.collect(self)
        self.time -= 1#se resta 1 al tiempo cada vez que se da un step
    
    #Función para saber si hay un agente cerca de una posición 
    #se implementó para prevenir que las roombas se atoraran si es que salía un obstáculo enfrente de ellas al iniciar la simulación
    def is_agent_nearby(self, pos):
        neighbors = self.grid.get_neighborhood(
            pos,
            moore=True,
            include_center=False
    )
    
        for neighbor in neighbors:
            agents_in_cell = self.grid.get_cell_list_contents([neighbor])
            for agent in agents_in_cell:
                if isinstance(agent, RandomAgent):
                    return True
    
        return False


    