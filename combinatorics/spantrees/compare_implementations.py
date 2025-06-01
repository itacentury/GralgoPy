import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
parent_directory = current_file_path.parent.parent.parent
sys.path.append(str(parent_directory))

import networkx as nx
import timeit

from structs.random_graph_generator import GenerateRandomGraph
from mst import PrimAlgorithm, KruskalAlgorithm

def main() -> None:
    generate_random_graph = GenerateRandomGraph(500, 50)
    graph: nx.Graph = generate_random_graph.generate()

    prim = PrimAlgorithm(graph)
    kruskal = KruskalAlgorithm(graph)
    
    iterations = 100
    # iterations = 5 -> 0,53 seconds
    # iterations = 100 -> 8,8 seconds
    time = timeit.timeit(lambda: prim.run(), number=iterations)
    print(f"Ausfuehrungszeit der eigenen prim Implementierung: {time} Sekunden")

    # iterations = 5 -> 0,45 seconds
    # iterations = 100 -> 6,2 seconds
    time = timeit.timeit(lambda: nx.minimum_spanning_tree(graph, algorithm="prim"), number=iterations)
    print(f"Ausfuehrungszeit der Networkx prim Implementierung: {time} Sekunden")

    iterations = 100
    # iterations = 5 -> 0,60 seconds
    # iterations = 100 -> 9,8 seconds
    time = timeit.timeit(lambda: kruskal.run(), number=iterations)
    print(f"Ausfuehrungszeit der eigenen kruskal Implementierung: {time} Sekunden")

    # iterations = 5 -> 0,80 seconds
    # iterations = 100 -> 10 seconds
    time = timeit.timeit(lambda: nx.minimum_spanning_tree(graph, algorithm="kruskal"), number=iterations)
    print(f"Ausfuehrungszeit der Networkx kruskal Implementierung: {time} Sekunden")

if __name__ == "__main__":
    main()