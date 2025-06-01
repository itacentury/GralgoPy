import random
import networkx as nx
import gurobipy as gp
import matplotlib.pyplot as plt

from gurobipy import GRB
from networkx.algorithms import bipartite
from typing import Tuple, List, Dict, Union

def create_weighted_bipartite_graph(n: int, p: float) -> nx.Graph:
    # Erstellen eines zufälligen bipartiten Graphen mit n Knoten in beiden Partitionen und einer Kantenwahrscheinlichkeit p
    graph: nx.Graph = bipartite.random_graph(n, n, p)
    # Zuweisen zufälliger Gewichte zwischen 1 und 15 zu jeder Kante im Graphen
    for u, v in graph.edges():
        graph.edges[u, v]['weight'] = random.randint(1, 15)
    return graph

def solve_maximum_matching(graph: nx.Graph) -> Tuple[gp.Model, gp.Var]:
    # Initialisieren des Optimierungsmodells
    model = gp.Model()
    # Hinzufügen von Variablen für jede Kante im Graphen, kontinuierlich zwischen 0 und 1
    variables: gp.Var = model.addVars(graph.edges(), vtype=GRB.BINARY, name='x')

    # Festlegen der Zielfunktion zur Maximierung der Summe der gewichteten Kanten im Matching
    model.setObjective(
        gp.quicksum(variables[u, v] * graph[u][v]['weight'] for u, v in graph.edges()),
        GRB.MAXIMIZE
    )

    # Hinzufügen von Beschränkungen, um sicherzustellen, dass jeder Knoten in genau einer
    # Kante des Matchings enthalten ist
    model.addConstrs(variables.sum(u, '*') == 1 for u in bipartite.sets(graph)[0])
    model.addConstrs(variables.sum('*', v) == 1 for v in bipartite.sets(graph)[1])

    # Optimieren des Modells
    model.optimize()
    return model, variables

def visualize_solution(graph: nx.Graph, selected_edges: List[Tuple[int, int]]):
    # Festlegen der Farben der Kanten basierend darauf, ob sie im optimalen Matching ausgewählt wurden
    edge_colors: List[str] = ['red' if edge in selected_edges else 'gray' for edge in graph.edges()]
    # Erstellen einer Positionierung der Knoten für die Zeichnung
    # pos: Dict[Union[int, str], Tuple[float, float]] = nx.spring_layout(graph)
    pos = nx.drawing.layout.bipartite_layout(graph, bipartite.sets(graph)[0])
    # Zeichnen des Graphen mit spezifizierten Farben und Positionen
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', edge_color=edge_colors)

    # Hinzufügen von Kantenbeschriftungen, die die Gewichte anzeigen
    edge_labels: Dict[Tuple[Union[int, str], Union[int, str]], float] = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    plt.show()

def main() -> None:
    graph: nx.Graph = create_weighted_bipartite_graph(4, 0.8)
    # Lösen des Maximum-Matching-Problems für den erstellten Graphen
    model, variables = solve_maximum_matching(graph)

    # Auswahl der Kanten, die im optimalen Matching enthalten sind
    selected_edges: List[Tuple[int, int]] = []
    if model.status == GRB.OPTIMAL:
        selected_edges = [(u, v) for u, v in graph.edges() if variables[u, v].x > 0.5]

    visualize_solution(graph, selected_edges)

if __name__ == "__main__":
    main()
