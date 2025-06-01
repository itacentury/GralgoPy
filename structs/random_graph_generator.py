import random
import networkx as nx

from itertools import combinations

class GenerateRandomGraph:
    def __init__(self, n: int, p: int) -> None:
        # Anzahl der Knoten im Graphen
        self.n: int = n
        # Wahrscheinlichkeit (in Prozent) einer Kante zwischen zwei Knoten
        self.p: int = p
        self.graph: nx.Graph = None

    def generate(self) -> nx.Graph:
        self.graph = nx.empty_graph(self.n)

        # Überprüfung, ob die Wahrscheinlichkeit p im gültigen Bereich liegt
        if self.p > 100 or self.p < 0:
            # Rückgabe des leeren Graphen, falls p ungültig ist
            return self.graph

        # Iteration über alle möglichen Kombinationen von zwei Knoten im Graphen
        for node1, node2 in combinations(range(self.n), 2):
            # Entscheidung, ob eine Kante zwischen node1 und node2 basierend auf der Wahrscheinlichkeit p hinzugefügt wird
            if random.randint(0, 100) < self.p:
                # Hinzufügen einer Kante mit zufälligem Gewicht zwischen 1 und 10
                self.graph.add_edge(node1, node2, weight=random.randint(1,10))
        return self.graph
