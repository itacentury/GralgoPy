import random
import networkx as nx
import gurobipy as gp
import matplotlib.pyplot as plt

from gurobipy import GRB
from itertools import combinations
from typing import Tuple, List, Dict

# Funktion zum Erstellen eines vollständigen Graphen mit zufälligen Distanzen zwischen den Knoten
def create_complete_graph(n: int, distance_range: Tuple[int, int] = (1, 15)) -> nx.Graph:
    graph: nx.Graph = nx.complete_graph(n)
    for u, v in graph.edges():
        graph.edges[u, v]['distance'] = random.randint(*distance_range)
    return graph

def build_gurobi_model(graph: nx.Graph) -> Tuple[gp.Model, gp.Var]:
    # Erstellt ein Dictionary mit den Distanzen als Werte
    dist: Dict[Tuple[int, int]] = {(u, v): graph[u][v]['distance'] for (u, v) in graph.edges()}
    # Erstellt eine Liste aller Knoten im Graphen
    capitals: List[int] = list(graph.nodes())

    m = gp.Model()
    # Fügt Variablen für jede Kante hinzu
    variables: gp.Var = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='x')
    # Aktualisiert die Variablen, um Symmetrie zu gewährleisten
    variables.update({(j, i): variables[i, j] for i, j in variables.keys()})
    # Stellt sicher, dass jeder Knoten genau zwei Verbindungen hat
    m.addConstrs(variables.sum(c, '*') == 2 for c in capitals)
    return m, variables, capitals

def subtourelim(model: gp.Model, where: int, capitals: List[int]) -> None:
    if where == GRB.Callback.MIPSOL:
        vals: Dict[Tuple[int, int], float] = model.cbGetSolution(model._vars)
        selected: gp.tuplelist = gp.tuplelist((i, j) for i, j in model._vars.keys() if vals[i, j] > 0.5)
        tour: List[int] = subtour(selected, capitals)
        # Wenn die Subtour nicht alle Knoten enthält, füge eine Lazy Constraint hinzu, um die Subtour zu eliminieren
        if len(tour) < len(capitals):
            model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2)) <= len(tour) - 1)

# Findet die kleinste subtour
def subtour(edges: gp.tuplelist, capitals: List[int]) -> List[int]:
    unvisited: List[int] = capitals[:]
    cycle: List[int] = capitals[:]
    while unvisited:
        thiscycle: List[int] = []
        neighbors: List[int] = unvisited
        while neighbors:
            current: int = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*') if j in unvisited]
        if len(thiscycle) <= len(cycle):
            cycle = thiscycle
    return cycle

def solve_tsp(graph: nx.Graph) -> List[Tuple[int, int]]:
    m, variables, capitals = build_gurobi_model(graph)
    m._vars = variables
    m.Params.lazyConstraints = 1
    m.optimize(lambda model, where: subtourelim(model, where, capitals))
    vals: Dict[Tuple[int, int], float] = m.getAttr('x', variables)
    selected: gp.tuplelist = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)
    tour: List[Tuple[int, int]] = subtour(selected, capitals)
    tour_edges = []
    for i in range(len(tour) - 1):
        tour_edges.append((tour[i], tour[i + 1]))
    tour_edges.append((tour[-1], tour[0]))
    return tour_edges

def visualize_solution(graph: nx.Graph, tour: List[int], dist: Dict) -> None:
    pos: Dict[int, Tuple[float, float]] = nx.spring_layout(graph)

    nx.draw_networkx_nodes(graph, pos)
    nx.draw_networkx_edges(graph, pos, alpha=0.5)
    nx.draw_networkx_labels(graph, pos)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=dist)

    nx.draw_networkx_edges(graph, pos, edgelist=tour, width=2, edge_color='r')  
    plt.show()

def main() -> None:
    n: int = 7
    graph: nx.Graph = create_complete_graph(n)
    dist: Dict[Tuple[int, int]] = {(u, v): graph[u][v]['distance'] for (u, v) in graph.edges()}
    tour: List[Tuple[int, int]] = solve_tsp(graph)
    print(f"Solution: {tour}")
    visualize_solution(graph, tour, dist) 

if __name__ == "__main__":
    main()