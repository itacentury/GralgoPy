import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
parent_directory = current_file_path.parent.parent.parent
sys.path.append(str(parent_directory))

from structs.union_find import UnionFind
from structs.priority_queue import PriorityQueue
from structs.random_graph_generator import GenerateRandomGraph

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

import networkx as nx

class Algorithm(ABC):
    def __init__(self, graph: nx.Graph) -> None:
        self.graph: nx.Graph = graph.copy()

    @abstractmethod
    def run(self) -> nx.Graph:
        pass
                                                                                                                                                                                                                                                                                                                                                                                                                                      
class PrimAlgorithm(Algorithm):
    def run(self, start: int = 0) -> nx.Graph:
        mst: nx.Graph = nx.empty_graph(self.graph.number_of_nodes())
        queue = PriorityQueue()
        # Setzt den Startknoten als besucht.
        visited = set([start])
        # Wörterbuch zur Speicherung der Vorgängerknoten.
        prev: Dict = {}

        # Fügt die anfänglichen Kanten zum Startknoten in die Warteschlange ein.
        self.add_initial_edges(start, queue, prev)

        while not queue.empty():
            # Entfernt und gibt den Knoten mit der niedrigsten Kante aus der Warteschlange zurück.
            u: int = queue.pop()
            if u not in visited:
                self.update_mst_and_queue(u, visited, mst, queue, prev)

        return mst
    
    def add_initial_edges(self, start: int, queue: PriorityQueue, prev: Dict):
        # Durchläuft alle Nachbarn des Startknotens.
        for neighbor, d in self.graph[start].items():
            # Fügt den Nachbarn mit dem Gewicht der Kante zur Warteschlange hinzu.
            queue.push(neighbor, d['weight'])
            # Speichert den Startknoten als Vorgänger des Nachbarn.
            prev[neighbor] = start

    def update_mst_and_queue(self, u: int, visited: set, mst: nx.Graph, queue: PriorityQueue, prev: Dict):
        # Fügt die Kante zum MST hinzu, wenn ein Vorgänger existiert.
        if u in prev:
            mst.add_edge(u, prev[u], weight=self.graph[u][prev[u]]['weight'])
        # Markiert den Knoten als besucht.
        visited.add(u)

        # Durchläuft alle Nachbarn des neuen Knotens.
        for v, data in self.graph[u].items():
            # Überprüft, ob der Nachbar nicht besucht wurde oder eine leichtere Kante existiert.
            if v not in visited and (v not in prev or data['weight'] < self.graph[v][prev[v]]['weight']):
                # Aktualisiert die Warteschlange und den Vorgänger für den Nachbarn.
                queue.push(v, data['weight'])
                prev[v] = u

class KruskalAlgorithm(Algorithm):
    def run(self) -> nx.Graph:
        mst: nx.Graph = nx.empty_graph(self.graph.number_of_nodes())
        union_find = UnionFind(list(self.graph.nodes()))

        # Sortiert die Kanten des Graphen nach ihrem Gewicht in aufsteigender Reihenfolge.
        sorted_edges: List[Tuple[int, int, Dict[str, int]]] = sorted(self.graph.edges(data=True), key=lambda x: x[2]['weight'])
        
        for u, v, data in sorted_edges:
            # Überprüft, ob die Hinzufügung der Kante einen Kreis im MST erzeugen würde.
            if union_find.find(u) != union_find.find(v):
                # Fügt die Kante zum MST hinzu, wenn kein Kreis entsteht.
                mst.add_edge(u, v, **data)
                # Vereinigt die beiden Knoten in der Union-Find-Datenstruktur.
                union_find.union(u, v)

        return mst

if __name__ == "__main__":
    generate_random_graph = GenerateRandomGraph(6, 50)
    graph: nx.Graph = generate_random_graph.generate()

    prim = PrimAlgorithm(graph)
    kruskal = KruskalAlgorithm(graph)

    min_span_tree_prim = prim.run()
    min_span_tree_kruskal = kruskal.run()

    print(graph)
    print(min_span_tree_prim)
    print(min_span_tree_kruskal)