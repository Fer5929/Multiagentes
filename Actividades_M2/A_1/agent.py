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

    def move(self):
        """Determines if the agent can move in the direction that was chosen."""
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
            
