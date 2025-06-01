import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
parent_directory = current_file_path.parent.parent.parent
sys.path.append(str(parent_directory))

import random
import gurobipy as gp
import networkx as nx

from networkx.algorithms import bipartite
from gurobipy import GRB
from structs.matroids import Matroid, PartitionMatroid
from typing import Dict, Tuple, Optional, Set

def weighted_matroid_intersection(left_matroid: Matroid, right_matroid: Matroid, weights: Dict[Tuple[int, int], float]) -> Tuple[Optional[Set[Tuple[int, int]]], Optional[float]]:
    # Initialisieren des Optimierungsmodells
    model = gp.Model()
    # In dieser Zeile wird für jede Kante in der Vereinigung der Kantenmengen von
    # zwei Matroiden (left_matroid und right_matroid) eine binäre Variable im Optimierungsmodell `model` erstellt. 
    # Diese Variablen repräsentieren, ob eine Kante in der Lösung des Problems enthalten ist (1) oder nicht (0).
    x: gp.Var = model.addVars(left_matroid.edges() | right_matroid.edges(), vtype=GRB.BINARY, name="x")
    # Festlegen der Zielfunktion zur Maximierung des Gewichts
    model.setObjective(x.prod(weights), GRB.MAXIMIZE)

    # Definition der Callback-Funktion für das Hinzufügen von Lazy Constraints
    def subtour_callback(model: gp.Model, where: int) -> None:
        if where == GRB.Callback.MIPSOL:
            sol: Dict[Tuple[int, int], float] = model.cbGetSolution(x)
            selected: Set[Tuple[int, int]] = {e for e in x if sol[e] > 0.5}

            # Für jede Lösung, die vom Solver gefunden wird (repräsentiert durch die binären Variablen x für die Kanten),
            # wird überprüft, ob die Menge der ausgewählten Kanten (selected) in jedem der beiden Matroide unabhängig ist.
            # Wenn die ausgewählten Kanten in einem der Matroide nicht unabhängig sind (d.h., die Unabhängigkeitsbedingung
            # verletzen), wird eine Lazy Constraint hinzugefügt.
            if not left_matroid.independent(selected):
                model.cbLazy(gp.quicksum(x[e] for e in selected) <= left_matroid.rank(selected))
            if not right_matroid.independent(selected):
                model.cbLazy(gp.quicksum(x[e] for e in selected) <= right_matroid.rank(selected))

    # Konfigurieren des Modells für die Verwendung von Lazy Constraints
    model._vars = x
    model.Params.lazyConstraints = 1
    # Optimieren des Modells
    model.optimize(subtour_callback)

    # Überprüfen des Optimierungsergebnisses und Rückgabe
    if model.status == GRB.OPTIMAL:
        max_weight_independent_set: Set[Tuple[int, int]] = {e for e in x if x[e].x > 0.5}
        max_weight: float = model.objVal
        return max_weight_independent_set, max_weight
    else:
        return None, None

def weighted_matching(graph: nx.Graph, weights: Dict[Tuple[int, int], float]) -> Tuple[Optional[Set[Tuple[int, int]]], Optional[float]]:
    # Ermitteln der Partitionen des bipartiten Graphen
    left_partition, right_partition = bipartite.sets(graph)
    # Erstellen von Partitionsmatroiden für beide Seiten
    left_partitions_list: list[Set[Tuple[int, int]]] = [{(u, v) for v in graph.neighbors(u)} for u in left_partition]
    right_partitions_list: list[Set[Tuple[int, int]]] = [{(u, v) for u in graph.neighbors(v)} for v in right_partition]
    
    left_matroid = PartitionMatroid(left_partitions_list)
    right_matroid = PartitionMatroid(right_partitions_list)

    # Berechnung der gewichteten Matroid-Intersection
    return weighted_matroid_intersection(left_matroid, right_matroid, weights)

def main() -> None:
    n: int = 10
    p: float = 0.7
    graph: nx.Graph = bipartite.random_graph(n, n, p)
    for u, v in graph.edges():
        graph[u][v]['weight'] = random.randint(1, 20)
    
    weights: Dict[Tuple[int, int], float] = nx.get_edge_attributes(graph, "weight")
    matching, calc_total_weight = weighted_matching(graph, weights)

    nx_matching = nx.max_weight_matching(graph)
    expec_total_weight: float = 0.0
    for node, partner in nx_matching:
        expec_total_weight += graph[node][partner]['weight']

    if matching:
        try:
            assert(expec_total_weight == calc_total_weight)
            print("Maximum weight matching:")
            for edge in matching:
                print(f"  {edge}: {weights[edge]}")
            print("Success: The calculated maximum weight matching matches the expected value.")
            print(f"The total weight is {calc_total_weight}")
        except AssertionError:
            print(f"Error: calculated max weight matching ({calc_total_weight}) is different from expected max weight matching ({expec_total_weight})")
    else:
        print("No matching found.")

if __name__ == "__main__":
    main()
