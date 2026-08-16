import networkx as nx
import random as rnd
import time  # Corretto (senza alias tm)
from loggers import setup_logger  # Assicurati che i percorsi di import siano corretti
from exceptions import GraphColException

log = setup_logger(name='DataGenerator')


def is_3_color(graph, timeout=2.0):  # Aumentato leggermente il timeout
    """
    We'll use backtraking for see if the graph is 3 colable
    if we go overtime we'll reaise a GraphException
    """
    start_time = time.time()
    colors = {}

    nodes = list(graph.nodes())

    def solve(node_idx):
        if (time.time() - start_time) > timeout:
            log.error(f"Timeout reached while checking 3-colorability per grafo con {graph.number_of_nodes()} nodi.")
            raise GraphColException("Timeout reached while checking 3-colorability",
                                    num_nodes=graph.number_of_nodes(),
                                    graph_type=type(graph).__name__)

        if node_idx == len(nodes):
            return True  # CORREZIONE: Maiuscolo per i booleani Python

        node = nodes[node_idx]
        used_color = {colors[neighbor] for neighbor in graph.neighbors(node) if neighbor in colors}

        for color in [0, 1, 2]:
            if color not in used_color:
                colors[node] = color
                if solve(node_idx + 1):
                    return True  # CORREZIONE: Maiuscolo
                del colors[node]
        return False

    return solve(0)


def generate_safe_graph(graph_type, num_nodes):
    """
    Generate a graph for our test
    """
    graph = None
    try:
        if graph_type == 'regular':
            log.info("Generating regular graph")
            # d è il grado dei nodi
            # d <= 2 il grafo è molto semplice ed è sempre 3 colorabile
            # d >= 5 il grafo è denso e intricato, quindi è più probabile che non sia 3 colorabile
            # Lo sweet spot per avere grafi 3 colorabili è d = 3 o d = 4
            d = rnd.choice([3, 4])
            graph = nx.random_regular_graph(d, num_nodes)

        elif graph_type == 'erdos_renyi':
            log.info("Generating erdos_renyi graph")
            # stabilisco una probabilità continua p in [0, 1], ovvero che un arco esista tra 2 nodi qualsiasi
            # per addestrare la rete neurale ai casi più complessi la alleniamo in casi in cui
            # il grado medio dei grafi oscilli tra un intervallo stretto intorno il 4.7
            # questo perché per i grafi di tipo erdos_renyi se si supera la soglia dl 4.7
            # la risoluzione del problema diventa impossibile
            p = rnd.uniform(3 / num_nodes, 6 / num_nodes)
            graph = nx.erdos_renyi_graph(num_nodes, p)

        return graph

    except nx.NetworkXError as e:
        log.warning(f"Impossibile generare grafo di tipo {graph_type} con {num_nodes} nodi. Errore: {e}")
        return None