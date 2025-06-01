import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
parent_directory = current_file_path.parent.parent.parent
sys.path.append(str(parent_directory))

import networkx as nx
import matplotlib.pyplot as plt
import random

from typing import Set, Dict, Optional
from structs.matroids import PartitionMatroid, UnweightedGraphMatroid

class Algorithm:
    def __init__(self, M1: UnweightedGraphMatroid, M2: PartitionMatroid) -> None:
        self.M1: UnweightedGraphMatroid = M1
        self.M2: PartitionMatroid = M2
        self.G: Optional[nx.DiGraph] = None

    def run(self) -> Set:
        # Starte mit einer leeren unabhängigen Menge
        I = set()

        while True:
            # Erstelle einen Graphen basierend auf der aktuellen Menge I
            self.build_graph(I)
            # Füge Kanten hinzu, die mögliche "Verbesserungen" von I darstellen
            self.intersect(I)

            try:
                # Versuche, einen kürzesten Pfad im Graphen von der Quelle ("S") zur Senke ("T") zu finden.
                path = nx.shortest_path(self.G, "S", "T")
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                # Wenn kein Pfad gefunden wird, ist die aktuelle Menge I maximal unabhängig und der Algorithmus bricht ab.
                break

            # Aktualisiere die unabhängige Menge I durch die symmetrische Differenz mit dem gefundenen Pfad.
            I = I.symmetric_difference(path)

        # Gib die maximale unabhängige Menge zurück
        return I
    
    def build_graph(self, I: Set) -> None:
        # Erstellt einen gerichteten Graphen G, der mögliche Erweiterungen der unabhängigen Menge I darstellt.
        self.G = nx.DiGraph()

        # Füge Kanten von der Quelle "S" zu Elementen hinzu, die zu I hinzugefügt werden können,
        # ohne die Unabhängigkeit in M1 zu verletzen.
        for e in self.M1.edges() - I:
            if self.M1.independent(I | {e}):
                self.G.add_edge("S", e)
        # Füge Kanten von Elementen zur Senke "T" hinzu, die zu I hinzugefügt werden können,
        # ohne die Unabhängigkeit in M2 zu verletzen.
        for e in self.M2.edges() - I:
            if self.M2.independent(I | {e}):
                self.G.add_edge(e, "T")
    
    def intersect(self, I: Set) -> None:
        # Fügt Kanten zu G hinzu, die mögliche "Austausch"-Operationen darstellen, um I zu verbessern.
        for e1 in I:
            for e2 in self.M1.edges() - I:
                # Wenn das Entfernen von e1 und Hinzufügen von e2 in M1 nicht unabhängig ist,
                # aber das Hinzufügen von e2 allein zu I in M1 unabhängig ist, füge eine Kante (e1, e2) hinzu.
                if not self.M1.independent(I - {e1} | {e2}) and self.M1.independent(I | {e2}):
                    self.G.add_edge(e1, e2)
            for e2 in self.M2.edges() - I:
                # Analog für M2, aber mit umgekehrter Kantenrichtung (e2, e1).
                if not self.M2.independent(I - {e1} | {e2}) and self.M2.independent(I | {e2}):
                    self.G.add_edge(e2, e1)
    
def generate_random_graph(n_nodes: int, p_edge: float) -> nx.Graph:
    graph: nx.Graph = nx.gnp_random_graph(n_nodes, p_edge)
    return graph

def assign_random_colors(graph: nx.Graph, n_colors: int) -> Dict:
    colors = {}
    for edge in graph.edges():
        colors[edge] = random.randint(1, n_colors)
    return colors

def main() -> None:
    n_nodes: int = 10
    n_colors: int = 5 
    p_edge: float = 0.3

    graph = generate_random_graph(n_nodes, p_edge)
    colors = assign_random_colors(graph, n_colors)

    M1 = UnweightedGraphMatroid(graph)
    partitions = [{
        edge for edge, color in colors.items() if color == c
        } for c in set(colors.values())
    ]
    M2 = PartitionMatroid(partitions)

    algorithm = Algorithm(M1, M2)
    rainbow_forest = algorithm.run()
    valid_rainbow_forest = [e for e in rainbow_forest if isinstance(e, tuple) and len(e) == 2]
    print("Rainbow Forest:", valid_rainbow_forest)

    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', font_weight='bold')
    nx.draw_networkx_edges(graph, pos, edgelist=valid_rainbow_forest, edge_color=[colors[e] for e in valid_rainbow_forest], width=2)
    plt.show()

if __name__ == "__main__":
    main()