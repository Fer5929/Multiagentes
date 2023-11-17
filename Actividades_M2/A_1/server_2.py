from mesa import DataCollector
from model import RandomModel, ObstacleAgent, DirtyAgent, ChargerAgent
from mesa.visualization import CanvasGrid, BarChartModule, TextElement,ChartModule
from mesa.visualization import ModularServer

def agent_portrayal(agent):
    if agent is None: return
    #Define como se verán los agentes 
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "pink",
                 "r": 0.5}

    if (isinstance(agent, ObstacleAgent)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    
    elif isinstance(agent, DirtyAgent):  
        portrayal["Color"] = "brown"
        portrayal["Layer"] = 0
        portrayal["w"] = 1.0  
        portrayal["h"] = 1.0 
    
    elif isinstance(agent, ChargerAgent):  
        portrayal["Color"] = "orange"
        portrayal["Layer"] = 0
        portrayal["w"] = 1.0  
        portrayal["h"] = 1.0 

    return portrayal
#Se dan los parámetros del modelo para la simulación 
#numero de agentes y tamaño del grid junto con tiempo y cantidad de agentes sucios
model_params = {"N":1, "width":15, "height":10, "T":1000 , "initial_num_dirty": 10}

grid = CanvasGrid(agent_portrayal, 15, 10, 500, 500)

#gráfica de steps por agente
bar_chart = BarChartModule(
    [{"Label":"Steps", "Color":"pink"}], 
    scope="agent", sorting="ascending", sort_by="Steps")

#gráfica de steps por dirty agent
dirty_chart=ChartModule(
    [{"Label":"Trash", "Color":"brown", "y":"Trash"}],
    data_collector_name="datacollector",
)

#timer
class TimeElement(TextElement):
    def render(self, model):
        return f"Time: {model.time}"

#porcentaje de suciedad restante 
class DirtElement(TextElement):
    def render(self, model):
        total_dirty = sum(1 for agent in model.schedule.agents if isinstance(agent, DirtyAgent))
        initial_dirty = model.initial_num_dirty  # Add a variable to store the initial count
        remaining_dirty = total_dirty  # Calculate the remaining dirty agents
        percentage_remaining = (remaining_dirty / initial_dirty) * 100
        return f"Dirt Remaining: {percentage_remaining:.2f}%"

#se crea el servidor con todos los elementos 
server = ModularServer(RandomModel, [TimeElement(),DirtElement(),grid, bar_chart,dirty_chart], "Rooooooombaaaaa", model_params)
                       
server.port = 8521 # The default
server.launch()