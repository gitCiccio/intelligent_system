import networkx as nx
import random as rnd
import time as tm

from matplotlib import colors
from sympy import true

from loggers import setup_logger
from exceptions import  GraphColException

log = setup_logger(name='DataGenerator')

"""
    We'll use backtraking for see if the graph is 3 colable
    if we go overtime we'll reaise a GraphException
    """
def is_3_color(graph, timeout=0.5):

    start_time = tm.time()
    colors = {}
    nodes = graph.nodes()

    def solve(node_idx):

        if (tm.time() - start_time) > timeout:
            log.error("Timeout reached while checking 3-colorability")
            raise GraphColException("Timeout reached while checking 3-colorability", num_nodes=graph.number_of_nodes(), graph_type=type(graph).__name__)

        if node_idx == len(nodes):
            return true

        node = nodes[node_idx]
        used_color = {colors[neighbor] for neighbor in graph.neighbors(node) if neighbor in colors}

        for color in [0, 1, 2]:
            if color not in used_color:
                colors[node] = color
                if solve(node_idx+1):
                    return true
                del colors[node]
        return False

    return solve(0)

"""
Generate a graph for our test
"""
def generate_safe_graph(graph_type, num_nodes):
    graph = None
    try:
        if graph_type == 'regular':
            #   - Se graph_type == 'regular': scegli un grado d (es. 3 o 4) e usa nx.random_regular_graph
            log.info("Generating regular graph")
            # d è il grado dei nodi
            # d <= 2 il grafo è molto semplice ed è sempre 3 colorabile
            # d >= 5 il grafo è denso e intricato, quindi è più probabile che non sia 3 colorabile
            # Lo sweet spot per avere grafi 3 colorabili è d = 3 o d = 4
            d = rnd.choice([3, 4])
            graph = nx.random_regular_graph(d, num_nodes)
        elif  graph_type == 'erdos_renyi':
            #   - Se graph_type == 'erdos_renyi': crea un grafo con p casuale attorno alla phase transition (es. p = random.uniform(3/num_nodes, 6/num_nodes))
            log.info("Generating erdos_renyi graph")
            # stabilisco una probabilità continua p in [0, 1], ovvero che un arco esista tra 2 nodi qualsiasi
            # per addestrare la rete neurale ai casi più complessi la alleniamo in casi in cui
            # il grado medio dei grafi oscilli tra un intervallo stretto intorno il 4.7
            # questo perché per i grafi di tipo erdos_renyi se si supera la soglia dl 4.7
            # il la risoluzione del problema diventa impossibile
            
            p = rnd.uniform(3/num_nodes, 6/num_nodes)
            graph = nx.erdos_renyi_graph(num_nodes, p)
        return graph
    except nx.NetworkXError as e:
        # Dentro except nx.NetworkXError:
        #   - Usa logger.warning(...) per segnalare che la topologia era impossibile.
        #   - return None
        log.error(f"Failed to generate graph of type {graph_type} with {num_nodes} nodes", graph_type=graph_type, num_nodes=num_nodes)
        return None


