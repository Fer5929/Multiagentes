from queue import Queue
from mesa import Agent

class RandomAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model, battery=100):
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
    
    def set_initial_position(self, pos):
        # Set the initial position when the agent is placed on the grid
        self.initial_position = pos
    
 



    def move(self):

        if self.battery<=26:
            print(self.initial_position)
            if self.pos != self.initial_position:
                # Find the next step to move towards the initial position
                next_move = self.find_next_step_to_initial()
                if self.model.grid.is_cell_empty(next_move) or self.check_for_obstacle(next_move):
                    self.model.grid.move_agent(self, next_move)
                    self.battery -= 1
            else:
                next_move = self.initial_position
                #If the agent is in same cell as Charger
                print(self.battery)
                agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
                charger_agent = [agent for agent in agents_in_cell if isinstance(agent, ChargerAgent)]
                if charger_agent:
                    while self.battery<20:
                        print("charging",{self.battery})
                        self.battery += 5
                        next_move = self.initial_position
        else:
        # Determine if the agent can move in the direction that was chosen.
            possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=True
        )
  
            
            # Checks which grid cells are empty
            freeSpaces = list(map(self.model.grid.is_cell_empty, possible_steps))

            # Checks which grid cells contain DirtyAgents
            dirtySpaces = [any(isinstance(agent, DirtyAgent) for agent in self.model.grid.get_cell_list_contents(pos)) for pos in possible_steps]

            # Combine freeSpaces and dirtySpaces to create a list of valid moves
            valid_moves = [p for p, f, d in zip(possible_steps, freeSpaces, dirtySpaces) if f or d]

            # Check if there are any valid moves
            if valid_moves:
                # Check if there's a DirtyAgent in the valid moves
                dirty_move = [move for move in valid_moves if any(isinstance(agent, DirtyAgent) for agent in self.model.grid.get_cell_list_contents(move))]

                if dirty_move:
                    # Prioritize moving to a cell with a DirtyAgent
                    next_move = self.random.choice(dirty_move)
                else:
                    # If no DirtyAgents in valid moves, move randomly to an empty cell
                    empty_cells = [move for move in valid_moves if self.model.grid.is_cell_empty(move)]
                    next_move = self.random.choice(empty_cells) if empty_cells else self.pos
            else:
            # If there are no valid moves, stay in the current cell
                next_move = self.pos

       
        
        # Now move:
        self.model.grid.move_agent(self, next_move)
        self.steps_taken += 1
        self.battery -= 1
        
    def find_next_step_to_initial(self):
        # Implement BFS to find the next step towards the initial position
        visited = set()
        q = Queue()
        q.put(self.pos)
        visited.add(self.pos)

        while not q.empty():
            current_pos = q.get()

            for next_pos in self.model.grid.get_neighborhood(
                current_pos,
                moore=True,
                include_center=True
            ):
                if next_pos not in visited:
                    visited.add(next_pos)
                    q.put(next_pos)

                    # Check if the next position is closer to the initial position
                    if self.calculate_distance(next_pos) < self.calculate_distance(current_pos) and not self.check_for_obstacle(next_pos) and not self.check_for_RandomAgent(next_pos):
                        return next_pos

        # If no valid step is found, return the current position
        return self.pos


    def calculate_distance(self, pos):
        return abs(pos[0] - self.initial_position[0]) + abs(pos[1] - self.initial_position[1])
    
    def check_for_obstacle(self, pos):
        # Check if the position contains an obstacle agent
        cell_contents = self.model.grid.get_cell_list_contents([pos])
        for agent in cell_contents:
            if isinstance(agent, ObstacleAgent):
                return True
        return False

    def check_for_RandomAgent(self, pos):
        # Check if the position contains an Random agent
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

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # Check if the cell exists in the grid
        if self.model.grid.is_cell_empty(self.pos):
            return

        # Check if there is any RandomAgent sharing the cell with the DirtyAgent
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        random_agents = [agent for agent in agents_in_cell if isinstance(agent, RandomAgent)]

        # If there are RandomAgents in the cell, remove the DirtyAgent
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
            
