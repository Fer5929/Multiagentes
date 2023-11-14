from mesa import DataCollector
from model import RandomModel, ObstacleAgent, DirtyAgent, ChargerAgent
from mesa.visualization import CanvasGrid, BarChartModule, TextElement
from mesa.visualization import ModularServer

def agent_portrayal(agent):
    if agent is None: return
    
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "pink",
                 "r": 0.5}

    if (isinstance(agent, ObstacleAgent)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    
    elif isinstance(agent, DirtyAgent):  # Add this condition for DirtyAgent
        portrayal["Color"] = "brown"
        portrayal["Layer"] = 0
        portrayal["w"] = 1.0  # Width of the square
        portrayal["h"] = 1.0  # Height of the square
    
    elif isinstance(agent, ChargerAgent):  # Add this condition for DirtyAgent
        portrayal["Color"] = "orange"
        portrayal["Layer"] = 0
        portrayal["w"] = 1.0  # Width of the square
        portrayal["h"] = 1.0  # Height of the square

    return portrayal

model_params = {"N":5, "width":15, "height":10, "T":1000 , "initial_num_dirty": 10}

grid = CanvasGrid(agent_portrayal, 15, 10, 500, 500)

bar_chart = BarChartModule(
    [{"Label":"Steps", "Color":"pink"}], 
    scope="agent", sorting="ascending", sort_by="Steps")




class TimeElement(TextElement):
    def render(self, model):
        return f"Time: {model.time}"
    
class DirtElement(TextElement):
    def render(self, model):
        total_dirty = sum(1 for agent in model.schedule.agents if isinstance(agent, DirtyAgent))
        initial_dirty = model.initial_num_dirty  # Add a variable to store the initial count
        remaining_dirty = total_dirty  # Calculate the remaining dirty agents
        percentage_remaining = (remaining_dirty / initial_dirty) * 100
        return f"Dirt Remaining: {percentage_remaining:.2f}%"

server = ModularServer(RandomModel, [TimeElement(),DirtElement(),grid, bar_chart], "Random Agents", model_params)
                       
server.port = 8521 # The default
server.launch()