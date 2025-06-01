import sys
from pathlib import Path

current_file_path = Path(__file__).resolve()
parent_directory = current_file_path.parent.parent.parent
sys.path.append(str(parent_directory))

import matplotlib.pyplot as plt
import networkx as nx

from structs.random_graph_generator import GenerateRandomGraph
from mst import PrimAlgorithm, KruskalAlgorithm

def draw_graph(graph: nx.Graph, pos: dict, ax: plt.Axes, node_color: str, edge_color: str, title: str) -> None:
    labels = nx.get_edge_attributes(G=graph, name='weight')
    nx.draw(G=graph, pos=pos, ax=ax, with_labels=True, node_size=150, node_color=node_color, edge_color=edge_color)
    nx.draw_networkx_edge_labels(G=graph, pos=pos, ax=ax, edge_labels=labels)
    ax.set_title(label=title)

def draw_random_graphs() -> None:
    generate_random_graph = GenerateRandomGraph(6, 80)
    graph: nx.Graph = generate_random_graph.generate()
    
    prim = PrimAlgorithm(graph)
    kruskal = KruskalAlgorithm(graph)

    pos = nx.spring_layout(G=graph, seed=7)

    graph_data = [
        (graph, 'blue', 'skyblue', 'Graph'),
        (nx.minimum_spanning_tree(G=graph, algorithm="prim"), 'green', 'lightgreen', 'Minimum Spanning Tree'),
        (prim.run(), 'red', 'lightcoral', 'Own Prim Algo'),
        (kruskal.run(), 'darkgray', 'lightgray', 'Own Kruskal Algo')
    ]

    _, axes = plt.subplots(nrows=1, ncols=len(graph_data), figsize=(12, 6))

    for i, (graph, node_color, edge_color, title) in enumerate(graph_data):
        draw_graph(graph=graph, pos=pos, ax=axes[i], node_color=node_color, edge_color=edge_color, title=title)

    plt.tight_layout()
    plt.show()

def main() -> None:
    draw_random_graphs()

if __name__ == "__main__":
    main()