from model import RandomModel, ObstacleAgent, DirtyAgent, ChargerAgent
from mesa.visualization import CanvasGrid, BarChartModule
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
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0
        portrayal["w"] = 1.0  # Width of the square
        portrayal["h"] = 1.0  # Height of the square
    
    elif isinstance(agent, ChargerAgent):  # Add this condition for DirtyAgent
        portrayal["Color"] = "orange"
        portrayal["Layer"] = 0
        portrayal["w"] = 1.0  # Width of the square
        portrayal["h"] = 1.0  # Height of the square

    return portrayal

model_params = {"N":4, "width":15, "height":10}

grid = CanvasGrid(agent_portrayal, 15, 10, 500, 500)

bar_chart = BarChartModule(
    [{"Label":"Steps", "Color":"#AA0000"}], 
    scope="agent", sorting="ascending", sort_by="Steps")

server = ModularServer(RandomModel, [grid, bar_chart], "Random Agents", model_params)
                       
server.port = 8521 # The default
server.launch()