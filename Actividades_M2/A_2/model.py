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
            model_reporters={"Trash": lambda m: sum(1 for agent in m.schedule.agents if isinstance(agent, DirtyAgent))}#lleva cuenta de la basura en el modelo
        )

        #tiempo de simulacion
        self.T = T
        self.time=T

        # Function to generate random positions
        pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
        #list with all the boarder positions
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]
        #los agentes se van a colocar en posiciones random dentro de la lista de border
        random.shuffle(border)#se revuelve la lista de border
        for i in range(N):#se crean y colocan los agentes
            agent = RandomAgent(i, self)
            self.schedule.add(agent)
            rand=random.randint(0,len(border)-1)
            pos = border[i]
            while not self.grid.is_cell_empty(pos):
                pos = border[i]
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

        # lo mismo que los Obstaculos pero con la DirtyAgent
        for i in range(10):
            dirty = DirtyAgent(i + 3000, self)  
            self.schedule.add(dirty)
            pos = pos_gen(self.grid.width, self.grid.height)
            while not self.grid.is_cell_empty(pos):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(dirty, pos)
        
        #Se agrega uno por cada RandomAgent en la simulación en la posición inicial
        for agent in self.schedule.agents:
            if isinstance(agent, RandomAgent):
                charger = ChargerAgent(agent.unique_id + 4000, self)
                self.schedule.add(charger)
                self.grid.place_agent(charger, agent.pos)

        
        self.datacollector.collect(self)#se recolectan los datos del modelo

    def step(self):
        # La simulación se detendrá si el tiempo es 0 o si no hay DirtyAgents en la simulación
        if self.time <= 0 or not any(isinstance(agent, DirtyAgent) for agent in self.schedule.agents):
            self.running = False
            return
        print(f"Time remaining: {self.time}") 
        self.schedule.step()
        self.datacollector.collect(self)
        self.time -= 1#se reduce el tiempo en 1
    
    #Función para saber si hay un agente cerca de una posición
    #se creó para evitar obstáculos enfrente de las roombas al momento de iniciar el modelo con la finlaidad de que no se queden atoradas
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


    