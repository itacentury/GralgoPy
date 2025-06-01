import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
parent_directory = current_file_path.parent.parent.parent
sys.path.append(str(parent_directory))

import networkx as nx

from typing import List, Tuple
from structs.random_digraph_generator import GenerateRandomDigraph

class Algorithm:
    def __init__(self, graph: nx.DiGraph) -> None:
        self.graph: nx.DiGraph = graph.copy()

    def run(self, s: int, t: int) -> int:
        # Initialisieren des maximalen Flusses mit 0
        max_flow: int = 0
        
        # Wiederholen, bis kein Pfad mehr gefunden wird
        while(True):
            # Suchen eines Pfades von s nach t
            path: List[Tuple[int, int]] = self.find_path(s, t)

            # Wenn kein Pfad gefunden wurde, Rückgabe des maximalen Flusses
            if not path:
                return max_flow

            # Finden der minimalen Kapazität im gefundenen Pfad
            min_capacity: int = min(capacity for _, capacity in path if capacity > 0)
            # Aktualisieren des maximalen Flusses
            max_flow += min_capacity

            # Aktualisieren der Kapazitäten im Graphen entlang des Pfades
            for (node1, _), (node2, _) in zip(path[:-1], path[1:]):
                # Hinzufügen der Rückkante
                self.graph.add_edge(node2, node1, capacity=min_capacity)

                capacity: int = self.graph[node1][node2]['capacity']
                dif_capacity: int = capacity - min_capacity

                # Entfernen der ursprünglichen Kante
                self.graph.remove_edge(node1, node2)
                # Aktualisieren der Kante, falls noch Kapazität übrig ist
                if dif_capacity > 0:
                    self.graph.add_edge(node1, node2, capacity=dif_capacity)

    def find_path(self, s: int, t: int, path: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        # Initialisieren des Pfades
        if path is None:
            path = [(s, 0)]

        # Wenn Start- und Zielknoten gleich sind, Rückgabe des Pfades
        if s == t:
            return path

        # Durchlaufen aller Nachbarn des aktuellen Knotens
        for neighbor in self.graph.neighbors(s):
            capacity: int = self.graph[s][neighbor]['capacity']
            # Zyklen werden vermieden, indem überprüft wird, ob ein Nachbar bereits im Pfad enthalten ist,
            # bevor er hinzugefügt wird. Dies stellt sicher, dass kein Knoten mehr als einmal besucht wird,
            # wodurch die Bildung von Zyklen im Pfad verhindert wird.
            if not any(node == neighbor for node, _ in path):
                result_path: List[Tuple[int, int]] = self.find_path(neighbor, t, path + [(neighbor, capacity)])
                if result_path:
                    # Rückgabe des Pfades, wenn einer gefunden wurde
                    return result_path
        # Rückgabe eines leeren Pfades, falls kein Pfad gefunden wurde
        return []

def main() -> None:
    generate_random_digraph = GenerateRandomDigraph(n=10, p=60)
    graph = generate_random_digraph.generate()

    source: int = 0
    target: int = graph.number_of_nodes() - 1

    algorithm = Algorithm(graph)

    calculated_flow: int = algorithm.run(s=source, t=target)
    expected_flow, _ = nx.maximum_flow(graph.copy(), _s=source, _t=target)
    
    try:
        assert(calculated_flow == expected_flow)
        print("Success: The calculated maximum flow matches the expected value.")
        print(f"The maximum flow is {calculated_flow}")
    except AssertionError:
        print(f"Error: calculated flow ({calculated_flow}) is different from expected flow ({expected_flow})")

if __name__ == "__main__":
    main()