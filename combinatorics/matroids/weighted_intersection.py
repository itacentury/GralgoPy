import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
parent_directory = current_file_path.parent.parent.parent
sys.path.append(str(parent_directory))

import random
import networkx as nx

from networkx import bipartite
from typing import Dict, Tuple, Set, List
from structs.matroids import PartitionMatroid

class Algorithm:
    def __init__(self, graph: nx.Graph, weights: Dict[Tuple[int, int], float]) -> None:
        self.graph: nx.Graph = graph
        self.weights: Dict[Tuple[int, int], float] = weights
        self.weights_keys_set: Set[Tuple[int, int]] = set(weights.keys())
        self.M1, self.M2 = self.build_partition_matroids()

    def build_partition_matroids(self):
        # Ermitteln der Partitionen des bipartiten Graphen
        try:
            left_partition, right_partition = bipartite.sets(self.graph)
        except nx.AmbiguousSolution:
            print("Error! AmbiguousSolution.")
            left_partition, right_partition = [], []
        # Erstellen von Partitionsmatroiden für beide Seiten
        left_edge_sets: list[Set[Tuple[int, int]]] = [{(u, v) for v in self.graph.neighbors(u)} for u in left_partition]
        right_edge_sets: list[Set[Tuple[int, int]]] = [{(u, v) for u in self.graph.neighbors(v)} for v in right_partition]
        
        left_matroid = PartitionMatroid(left_edge_sets)
        right_matroid = PartitionMatroid(right_edge_sets)

        return left_matroid, right_matroid

    def run(self) -> Set:
        # Schritt 1
        X: List[Set[int]] = [set()]
        c1: Dict[Tuple[int, int], float] = self.weights.copy()
        c2: Dict[Tuple[int, int], float] = {e: 0 for e in self.weights}
        k: int = 0

        while True:
            # Schritt 2
            G_bar: nx.DiGraph = nx.DiGraph()
            # Dictionary für fundamentale Kreise in Matroid 1
            C1: Dict[int, Set[int]] = {}
            # Dictionary für fundamentale Kreise in Matroid 2
            C2: Dict[int, Set[int]] = {}
            for y in self.weights_keys_set - X[k]:
                # Ermitteln der Kanten, die die Unabhängigkeit der Matroide verletzen bzw.
                # ermitteln der fundamentalen Kreise C_i(X_k, y) für Matroid 1 und 2
                C1[y] = {x for x in X[k] | {y} if not self.M1.independent(X[k] | {y}) and self.M1.independent((X[k] | {y}) - {x})}
                C2[y] = {x for x in X[k] | {y} if not self.M2.independent(X[k] | {y}) and self.M2.independent((X[k] | {y}) - {x})}
            
            # Schritt 3
            # Ermitteln der Kanten für die Konstruktion von G_bar
            A1: Set[Tuple[int, int]] = {(x, y) for y in self.weights_keys_set - X[k] for x in C1[y] - {y}}
            A2: Set[Tuple[int, int]] = {(y, x) for y in self.weights_keys_set - X[k] for x in C2[y] - {y}}
            # Elemente, die zu X[k] hinzugefügt werden können (Matroid 1)
            S: Set[int] = {y for y in self.weights_keys_set - X[k] if self.M1.independent(X[k] | {y})}
            # Elemente, die zu X[k] hinzugefügt werden können (Matroid 2)
            T: Set[int] = {y for y in self.weights_keys_set - X[k] if self.M2.independent(X[k] | {y})}

            # Schritt 4
            # Wenn S und T leer sind, wurde eine maximale Lösung gefunden
            if not S and not T:
                break

            # Maximales c1-Gewicht in S
            m1: float = max(c1[y] for y in S) if S else float('-inf')
            # Maximales c2-Gewicht in T
            m2: float = max(c2[y] for y in T) if T else float('-inf')
            # Elemente in S mit maximalem c1-Gewicht
            S_bar: Set[int] = {y for y in S if c1[y] == m1}
            # Elemente in T mit maximalem c2-Gewicht
            T_bar: Set[int] = {y for y in T if c2[y] == m2}

            # Filtern der Kanten für A1_bar und A2_bar (reduzierte Kantenmengen)
            A1_bar: Set[Tuple[int, int]] = {(x, y) for (x, y) in A1 if c1[x] == c1[y]}
            A2_bar: Set[Tuple[int, int]] = {(y, x) for (y, x) in A2 if c2[x] == c2[y]}

            # Hinzufügen der Knoten und Kanten zu G_bar
            G_bar.add_nodes_from(self.weights_keys_set)
            G_bar.add_edges_from(A1_bar | A2_bar)
            
            # Schritt 5
            try:
                R: Set[Tuple[int, int]] = set()
                for s_node in S_bar:
                    # Ermitteln der Nachkommen von s_node in G_bar und Hinzufügen zu R
                    R.update(nx.descendants(G_bar, s_node) | {s_node})
            except nx.NodeNotFound:
                continue

            # Schritt 6
            if R & T_bar:
                P: List[Tuple[int, int]] = []
                found: bool = False
                for s_node in S_bar:
                    if found:
                        break
                    for t_node in T_bar:
                        try:
                            P = nx.shortest_path(G_bar, s_node, t_node)
                            found = True
                            break
                        except nx.NetworkXNoPath:
                            continue
                # Aktualisieren von X[k] basierend auf dem gefundenen Pfad P
                X.append((X[k] | set(P[::2])) - set(P[1::2]))
                k += 1

            # Schritt 7
            else:
                epsilon1: float = float("inf")
                edges_1: List[Tuple[int, int]] = [(x, y) for x, y in A1 if x in R and y not in R]
                if edges_1:
                    epsilon1 = min(c1[x] - c1[y] for x, y in edges_1)

                epsilon2: float = float("inf")
                edges_2: List[Tuple[int, int]] = [(x, y) for y, x in A2 if y in R and x not in R]
                if edges_2:
                    epsilon2 = min(c2[x] - c2[y] for x, y in edges_2)
                
                epsilon3: float = min(m1 - c1[y] for y in S - R) if S - R else float("inf")
                epsilon4: float = min(m2 - c2[y] for y in T & R) if T & R else float("inf")
                epsilon: float = min(epsilon1, epsilon2, epsilon3, epsilon4)

                # Schritt 8
                if epsilon < float("inf"):
                    for x in R:
                        c1[x] -= epsilon
                        c2[x] += epsilon
                # Wenn epsilon unendlich ist, wurde die maximale Lösung gefunden
                else:
                    break

        # Gebe die Menge mit dem maximalen Gewicht zurück und nicht immer die letzte Menge
        return self.get_max_weight_set(X)
    
    def get_max_weight_set(self, X: List[Set[int]]) -> Set[int]:
        # Funktion zum Berechnen des Gewichts einer Menge
        def set_weight(x: Set[int]) -> int:
            return sum(self.weights[edge] for edge in x)

        # Finden der Menge mit dem maximalen Gewicht
        max_weight_set = max(X, key=set_weight)
        return max_weight_set

def main() -> None:
    graph: nx.Graph = bipartite.random_graph(10, 10, 0.6)
    for u, v in graph.edges():
        graph[u][v]['weight'] = random.randint(1, 20)
    weights: Dict[Tuple[int, int], float] = nx.get_edge_attributes(graph, "weight")

    algorithm = Algorithm(graph, weights)
    result: Set[Tuple[int, int]] = algorithm.run()
    calculated_weight: float = sum(weights[edge] for edge in result)

    nx_matching: Set[Tuple[int, int]] = nx.max_weight_matching(graph)
    expected_weight: float = sum(graph[node][partner]['weight'] for node, partner in nx_matching)

    try:
        assert(expected_weight == calculated_weight)
        print("Maximum weight matching:")
        for edge in result:
            print(f"  {edge}: {weights[edge]}")
        print("Success: The calculated maximum weight matching matches the expected value.")
        print(f"The total weight is {calculated_weight}")
    except AssertionError:
        print(f"Error: calculated max weight matching ({calculated_weight}) is different from expected max weight matching ({expected_weight})")

if __name__ == "__main__":
    main()
