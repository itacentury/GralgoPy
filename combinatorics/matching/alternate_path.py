import random
import networkx as nx
import matplotlib.pyplot as plt

from networkx.algorithms import bipartite
from typing import Tuple, List

class BlossomAlgorithm:
    def __init__(self, graph: nx.Graph) -> None:
        self.graph: nx.Graph = graph.copy()
        self.starting_node: int = random.choice(list(self.graph.nodes))
        self.matching: nx.Graph = nx.Graph()

    def run(self) -> None:
        # Durchlaufen aller Nachbarn des Startknotens
        for neighbor in self.graph.neighbors(self.starting_node):
            self.traverse_path(neighbor)

        self.create_matching()

    def traverse_path(self, node: int, label_index: int = 0) -> None:
        # Zuweisung eines Labels (inner/outer) zum aktuellen Knoten
        self.graph.nodes[node]["label"], label_index = self.label_node(label_index)

        # Durchlaufen aller Nachbarn des aktuellen Knotens
        for neighbor in self.graph.neighbors(node):
            # Überspringen, wenn der Nachbar bereits gelabelt ist
            if self.graph.nodes[neighbor]["label"] in ["inner", "outer"]:
                continue
            # Rekursiver Aufruf für den Nachbarknoten
            self.traverse_path(neighbor, label_index)

    def label_node(self, label_index: int) -> Tuple[str, int]:
        label: str = "inner"
        # Wechsel zu "outer" bei geradem Index
        if label_index % 2 == 0:
            label = "outer"

        # Erhöhung des Index für das nächste Label
        label_index += 1
        return label, label_index
    
    def create_matching(self) -> None:
        # Durchlaufen aller Kanten des Graphen
        for u, v in self.graph.edges():
            # Überprüfung der Label und ob die Knoten bereits im Matching sind
            if (self.graph.nodes[u]["label"] == "inner" and
                self.graph.nodes[v]["label"] == "outer" and
                u not in self.matching and v not in self.matching):
                # Hinzufügen der Kante zum Matching
                self.matching.add_edge(u, v)
                # Markierung der Kante als Matching
                self.graph[u][v]["matching"] = True

def main() -> None:
    graph = bipartite.random_graph(4, 4, 0.8)

    for (u, v) in graph.edges():
        graph.edges[u, v]['weight'] = random.randint(1, 15)

    nx.set_node_attributes(graph, "", "label")
    nx.set_edge_attributes(graph, False, "matching")

    blossom_algorithm = BlossomAlgorithm(graph)
    blossom_algorithm.run()

    # Plotting
    edge_colors: List[str] = []
    for edge in blossom_algorithm.graph.edges(data=True):
        if edge[2].get('matching', False):
            edge_colors.append('red')
        else:
            edge_colors.append('gray')

    pos = nx.spring_layout(blossom_algorithm.graph)
    _, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

    nx.draw(blossom_algorithm.graph, pos, with_labels=True, 
            labels=nx.get_node_attributes(blossom_algorithm.graph, "label"), 
            edge_color=edge_colors, ax=axes[0])
    axes[0].set_title("Original Graph")

    nx.draw(blossom_algorithm.matching, pos, with_labels=True, 
            labels=nx.get_node_attributes(blossom_algorithm.matching, "label"), 
            ax=axes[1])
    axes[1].set_title("Matching")

    plt.show()

if __name__ == "__main__":
    main()