import random
import networkx as nx
import gurobipy as gp

from gurobipy import GRB
from typing import Tuple, List, Set, Dict

# Erstellt einen vollständigen, gewichteten Graphen mit zufälligen Kantengewichten.
def create_weighted_complete_graph(n: int) -> nx.Graph:
    graph: nx.Graph = nx.complete_graph(n)
    for u, v in graph.edges():
        graph.edges[u, v]['distance'] = random.randint(1, 15)
    return graph

def solve_mst_with_gurobi(graph: nx.Graph) -> Tuple[gp.Model, gp.tupledict]:
    # Initialisiert ein neues Optimierungsmodell.
    model = gp.Model()

    # Erstellt eine binäre Variable x[u,v] für jede Kante (u,v) im Graphen.
    # Damit wird dann angegeben, ob eine Kante zur Lösung gehört oder nicht.
    edge_vars: gp.tupledict = model.addVars(graph.edges(), vtype=GRB.BINARY, name='x')

    # Definiert die Zielfunktion: Minimiere die Summe der Kantengewichte des MST.
    # Dabei ist edge_vars[u,v] entweder 0 oder 1, was bewirkt dass nur die Gewichte
    # der Kanten der Lösung summiert werden.
    model.setObjective(
        gp.quicksum(edge_vars[u, v] * graph[u][v]['distance'] for u, v in graph.edges()), 
        GRB.MINIMIZE
    )

    # Fügt eine Einschränkung hinzu, um sicherzustellen, dass die Anzahl der ausgewählten Kanten gleich
    # der Anzahl der Knoten minus 1 ist. Definition eines Spannbaumes.
    model.addConstr(gp.quicksum(edge_vars) == graph.number_of_nodes() - 1)

    # Callback-Funktion zur Eliminierung von Subtouren.
    def subtour_elim(model: gp.Model, where: int) -> None:
        if where == GRB.Callback.MIPSOL:
            # Holt die Lösung der Variablen.
            vals: Dict = model.cbGetSolution(model._vars)
            # Wählt die Kanten aus, die in der aktuellen Lösung enthalten sind.
            selected: gp.tupledict = gp.tuplelist((i, j) for i, j in model._vars.keys() if vals[i, j] > 0.5)
            # Findet die Komponenten (Subtouren) im Graphen der ausgewählten Kanten.
            components: List[Set] = nx.connected_components(nx.Graph(selected))
            # Falls die Lösung mehr als eine Komponente besitzt, gibt es mehrere Subtouren.
            # Das heißt dass es mehrere nicht zusammenhängende Bäume gibt. Diese wollen wir eliminieren.
            if len(list(components)) > 1:
                # Für jede Komponente (Subtour), füge eine Lazy Constraint hinzu, um die Subtour zu eliminieren.
                for S in components:
                    model.cbLazy(gp.quicksum(model._vars[i, j] for i in S for j in S if i < j) <= len(S) - 1)

    # Speichert die Kantenvariablen im Modell für den Callback-Zugriff.
    model._vars = edge_vars
    model.Params.lazyConstraints = 1
    model.optimize(subtour_elim)  
    return model, edge_vars

def main() -> None:
    graph: nx.Graph = create_weighted_complete_graph(7)
    nx_mst: nx.Graph = nx.minimum_spanning_tree(graph, weight="distance")

    gurobi_model, gurobi_vars = solve_mst_with_gurobi(graph)

    print("NetworkX Minimum Spanning Tree:")
    for u, v in nx_mst.edges():
        weight: int = nx_mst[u][v]['distance']
        print(f"({u}, {v}): {weight}")
    print(f"Total weight of NetworkX MST: {nx_mst.size(weight='distance')}")

    if gurobi_model.status == GRB.OPTIMAL:
        print("\nGurobi Minimum Spanning Tree:")
        for u, v in graph.edges():
            if gurobi_vars[u, v].x > 0.5:
                weight: int = graph[u][v]['distance']
                print(f"({u}, {v}): {weight}")
        print(f"Total weight of Gurobi MST: {gurobi_model.objVal}")

    gurobi_model.dispose()
    gp.disposeDefaultEnv()

if __name__ == "__main__":
    main()