from queue import Queue
from mesa import Agent

class RandomAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, battery=100, steps=0, clean=0):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.direction = 4
        self.steps_taken = 0
        self.battery = battery
        #variable to store the initial position
        self.initial_position = None
        self.steps = steps
        self.clean = clean
    
    def set_initial_position(self, pos):
        # Set the initial position when the agent is placed on the grid
        self.initial_position = pos
    
 



    def move(self):
        """
        Hace lo siguiente: revisa que haya batería disponible para moverse, en este caso se usó el valor de 26 dado que es el valor entero de la hipotenusa de una grid de 15 x10
        Si la batería es menor a 26 y la posición es diferente a la posición inicial, se mueve hacia la posición inicial
        Si la batería es menor a 100 y la posición es igual a la posición inicial, se carga la batería hasta que llegue a 100
        Si la batería es mayor a 100, se mueve aleatoriamente revisando si hay obstáculos que le impidan moverse al igual 
        que si hay alguna celda sucia, si es el caso se prioriza la limpieza de la misma siempre y cuando la batería sea mayor a 26

        """
        
        if self.battery <= 26 and self.pos != self.initial_position:
            # Move towards the initial position
            next_move = self.regresa() #llama al método para calcular como regresar a la posición inicial
            if next_move and (self.model.grid.is_cell_empty(next_move) or self.check_for_obstacle(next_move)):
                self.model.grid.move_agent(self, next_move)
                self.battery -= 1#disminuye la batería
                self.steps += 1#suma un paso al contador de pasos
        elif self.battery < 100 and self.pos == self.initial_position:
            # If at initial position, charge battery by 5 units per step, until it reaches 100
            print("charging",{self.battery})#imprime la batería antes y después en la consola de cada agente
            self.battery = min(100, self.battery + 5)
            print("charging",{self.battery})
            if self.battery >= 100:
                # Si hay batería entonces se puede mover
                possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=True
            )
  
                self.battery -= 1#como se va a mover se quita uno de batería

                # Checks which grid cells are empty
                freeSpaces = list(map(self.model.grid.is_cell_empty, possible_steps))

                # Checks which grid cells contain DirtyAgents
                dirtySpaces = [any(isinstance(agent, DirtyAgent) for agent in self.model.grid.get_cell_list_contents(pos)) for pos in possible_steps]

                # Combine freeSpaces and dirtySpaces to create a list of valid moves
                valid_moves = [p for p, f, d in zip(possible_steps, freeSpaces, dirtySpaces) if f or d]

                # Check if there are any valid moves
                if valid_moves:
                    # Revisa si hay DirtyAgents en los movimientos válidos
                    dirty_move = [move for move in valid_moves if any(isinstance(agent, DirtyAgent) for agent in self.model.grid.get_cell_list_contents(move))]

                    #clean es una variable que nos ayuda a quedarnos un step en el mismo espacio "limpiando"
                    if dirty_move:
                        #Si hay una celda vecina sucia

                        if self.clean == 1:#significa que se está limpiando 
                            next_move = self.pos#se queda ahí limpiando
                            self.clean=0#ya acabó de limpiar
                        else:
                        # de lo contrario ve a moverte a la celda a limpiar 
                            next_move = self.random.choice(dirty_move)
                            self.clean = 1.#se cambia el estado a limpiando
                            self.steps += 1#se aumenta porque si se mueve 
                        
                    else:
                        #sino hay un DirtyAgent cerca 
                        if self.clean == 0:
                            # sino se esta limpiando actualmente muevete a una celda libre
                            empty_cells = [move for move in valid_moves if self.model.grid.is_cell_empty(move)]
                            next_move = self.random.choice(empty_cells) if empty_cells else self.pos
                            self.steps += 1
                        elif self.clean == 1:
                            #si se esta limpiando quédate ahí
                            next_move = self.pos
                            self.clean = 0#acabó de limpiar
                            
                        
                else:
                # En caso de que no haya manera de moverse quédate ahí
                    next_move = self.pos
            else:
                next_move = self.initial_position #si no está en la posición inicial se mueve a ella

                        
                        
        else:
        # Determine if the agent can move in the direction that was chosen.
            possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=True
        )
  
            self.battery -= 1#disminuye la batería
            
            # Checks which grid cells are empty
            freeSpaces = list(map(self.model.grid.is_cell_empty, possible_steps))

            # Checks which grid cells contain DirtyAgents
            dirtySpaces = [any(isinstance(agent, DirtyAgent) for agent in self.model.grid.get_cell_list_contents(pos)) for pos in possible_steps]

            # Combine freeSpaces and dirtySpaces to create a list of valid moves
            valid_moves = [p for p, f, d in zip(possible_steps, freeSpaces, dirtySpaces) if f or d]

            # Check if there are any valid moves
            if valid_moves:
                #Revisa si hay DirtyAgents en los movimientos válidos
                dirty_move = [move for move in valid_moves if any(isinstance(agent, DirtyAgent) for agent in self.model.grid.get_cell_list_contents(move))]

                #misma lógica anterior
                if dirty_move:
                    if self.clean == 1:
                        next_move = self.pos
                        self.clean=0
                    else:
                        # Prioritize moving to a cell with a DirtyAgent
                        next_move = self.random.choice(dirty_move)
                        self.clean = 1
                        self.steps += 1
                else:
                        if self.clean == 0:
                            # If no DirtyAgents in valid moves, move randomly to an empty cell
                            empty_cells = [move for move in valid_moves if self.model.grid.is_cell_empty(move)]
                            next_move = self.random.choice(empty_cells) if empty_cells else self.pos
                            self.steps += 1
                        elif self.clean == 1:
                            next_move = self.pos
                            self.clean = 0
                            
                        
            else:
                next_move = self.pos

       
        
        # Now move:
        self.model.grid.move_agent(self, next_move)
        self.steps_taken += 1
        #self.battery -= 1
        print("steps:",{self.steps})
        
        
    def regresa(self):
        """
        Se usó la lógica de BFS para encontrar el camino de regreso al cargador. 
        """
        visited = set()#se guarda los nodos visitados
        q = Queue()#se crea una queue
        q.put(self.pos)#se agrega la posición actual
        visited.add(self.pos)#se agrega a los visitados
        #ahora lo que se hace es recorrer el grafo hasta encontrar la posición inicial

        while not q.empty():#mientras la queue no esté vacía
            current_pos = q.get()#se obtiene el primer elemento de la queue

            for next_pos in self.model.grid.get_neighborhood(
                current_pos,
                moore=True,
                include_center=True
            ):
                if next_pos not in visited:#si no está en los visitados
                    visited.add(next_pos)#se agrega a los visitados
                    q.put(next_pos)#se agrega a la queue

                    #Revisa si la posición a la que se va a mover es menor a la posición actual, si no hay obstáculos y si no hay un RandomAgent en esa posición
                    if self.calculate_distance(next_pos) < self.calculate_distance(current_pos) and not self.check_for_obstacle(next_pos) and not self.check_for_RandomAgent(next_pos):
                        return next_pos#regresa la posición a la que se va a mover

        # sino se queda ahí y se repite el proceso
        return self.pos


    def calculate_distance(self, pos):
        #cálculo de la distancia entre dos puntos
        return abs(pos[0] - self.initial_position[0]) + abs(pos[1] - self.initial_position[1])
    
    def check_for_obstacle(self, pos):
        # Revisa si hay algún obstáculo en la posición 
        cell_contents = self.model.grid.get_cell_list_contents([pos])
        for agent in cell_contents:
            if isinstance(agent, ObstacleAgent):
                return True
        return False

    def check_for_RandomAgent(self, pos):
        # Lo mismo pero para random agent
        cell_contents = self.model.grid.get_cell_list_contents([pos])
        for agent in cell_contents:
            if isinstance(agent, RandomAgent):
                return True
        return False

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.move()

class ObstacleAgent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass  


class DirtyAgent(Agent):
    """
    Agent that represents a dirty cell.
    """

    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)
        

    def step(self):
        
        if self.model.grid.is_cell_empty(self.pos):
            return

        #Si hay una roomba en la misma cedla se elimina ese DirtyAgent
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        random_agents = [agent for agent in agents_in_cell if isinstance(agent, RandomAgent)]

        
        if random_agents:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

class ChargerAgent(Agent):
    """
    Charger agent. Charges the agent while standing on it.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass  
            
