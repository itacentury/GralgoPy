import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
parent_directory = current_file_path.parent.parent.parent
sys.path.append(str(parent_directory))

import networkx as nx
from typing import Set

from structs.random_graph_generator import GenerateRandomGraph
from structs.matroids import Matroid, GraphMatroid

class Algorithm:
    def __init__(self, M: Matroid) -> None:
        self.M: Matroid = M

    def run(self):
        # Initialisierung der Grundmenge E und der unabhängigen Menge I
        E: Set = set(self.M.groundset)
        I: Set = set()

        # Solange E nicht leer ist
        while E:
            # Wähle ein Element x aus E mit minimalem Gewicht
            x: Set = self.M.minarg(E)
            # Wenn die Vereinigung von I und {x} unabhängig im Matroid ist, füge x zu I hinzu
            if self.M.independent(I | {x}):
                I.add(x)
            # Entferne x aus E
            E.remove(x)

        # Rückgabe der unabhängigen Menge I als Basis des Matroids
        return I

def main() -> None:
    random_graph = GenerateRandomGraph(6, 50)
    graph: nx.Graph = random_graph.generate()

    matroid = GraphMatroid(graph)

    algorithm = Algorithm(matroid)
    basis = algorithm.run()
    print(basis)

    mst: nx.Graph = nx.minimum_spanning_tree(graph)
    print(set(mst.edges))

if __name__ == "__main__":
    main()