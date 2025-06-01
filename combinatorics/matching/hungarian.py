import random
import math
import networkx as nx
import matplotlib.pyplot as plt

from networkx import bipartite
from typing import Set, Tuple, List, Dict

class Algorithm:
    def __init__(self, graph: nx.Graph) -> None:
        self.graph: nx.Graph = graph.copy()

    def calculate_slack(self, u: int, v: int, y: Dict[int, float]) -> float:
        # Berechne den Slack-Wert für eine Kante (u, v): y_u + y_v - w(u,v).
        # Differenz zwischen den Summen der Dualvariablen y[u] und y[v] und dem Kantengewicht w(u, v).
        return y[u] + y[v] - self.graph[u][v]['weight']

    def run(self) -> Set[Tuple[int, int]] | None:
        # Bestimme die zwei Knotenmengen L (linke Seite) und R (rechte Seite) des bipartiten Graphen
        L: Set[int] = set(n for n, d in self.graph.nodes(data=True) if d['bipartite'] == 0)
        R: Set[int] = set(self.graph) - L

        # Initialisiere duale Variablen y für L mit 0 und für R mit maximalem Kantengewicht.
        # Repräsentieren eine Art "Potenzial" für jeden Knoten. Sie werden iterativ angepasst.
        y: Dict[int, float] = {v: 0 for v in L}
        y.update({v: max((self.graph[u][v]['weight'] for u, v in self.graph.edges(v)), default=0) for v in R})

        # M ist die Menge der aktuellen Matching-Kanten (anfangs leer)
        M: Set[Tuple[int, int]] = set()

        while len(M) < len(L):
            # Menge der Knoten im aktuellen alternierenden Baum
            U: Set[int] = set()
            # Menge der Knoten in R, die von U erreicht werden können
            V: Set[int] = set()
            # Vorgängerknoten im alternierenden Baum
            T: Dict[int, int] = {}

            # Finde freie (ungematchte) Knoten in L
            free_L: Set[int] = {l for l in L if all((l, r) not in M and (r, l) not in M for r in R)}
            if not free_L:
                # Keine freien Knoten mehr -> Matching ist maximal
                break

            # Füge freie Knoten zu U hinzu
            U.update(free_L)
            # Initialisiere Vorgänger von freien Knoten als None
            T.update({l: None for l in free_L})

            # Initialisiere Slack-Werte für Knoten in R
            slack_value: Dict[int, float] = {v: float('inf') for v in R}
            # Berechnung der Slack-Werte für alle Kanten zwischen U und R
            for u in U & L:
                for v in R - U:
                    if self.graph.has_edge(u, v):
                        # Aktualisiere Slack-Werte
                        value: float = min(slack_value[v], self.calculate_slack(u, v, y))
                        slack_value[v] = value

            found_augmenting_path: bool = False
            # Innere Schleife zur Suche nach augmentierenden Pfaden
            while not found_augmenting_path:
                if all(v in V for v in R):
                    # Alle Knoten in R erreicht -> kein augmentierender Pfad
                    break

                # Delta: Berechnung des minimalen Slack-Wertes einer Kante zwischen U und einem Knoten in R,
                # der noch nicht in V ist.
                delta: float = min(slack_value[v] for v in R if v not in V)
                if math.isnan(delta): delta = 0

                # Anpassung der dualen Variablen um Delta
                for u in U:
                    y[u] -= delta
                for v in R:
                    if v in V:
                        y[v] += delta
                    else:
                        slack_value[v] -= delta

                # Wenn durch die Anpassung von y eine Kante den Slack-Wert 0 erreicht,
                # wird diese Kante zum alternierenden Baum hinzugefügt, und die Mengen U und V werden aktualisiert.
                for v in R:
                    # Slack-Wert von 0 bedeutet, dass der Knoten eine vielversprechende Erweiterung des Matchings
                    # darstellen könnte und noch nicht im alternierenden Baum V enthalten ist.
                    if slack_value[v] == 0 and v not in V:
                        V.add(v)
                        for u in L:
                            # Überprüfen ob es eine Kante zwischen u und v gibt und ob diese Kante ebenfalls einen Slack-Wert von 0 hat.
                            if self.graph.has_edge(u, v) and self.calculate_slack(u, v, y) == 0:
                                # Wenn der Knoten u bereits im alternierenden Baum U enthalten ist, bedeutet das, dass eine Kante gefunden wurde,
                                # die zwei Knoten innerhalb des Baums verbindet. In diesem Fall wird der Vorgänger des Knotens v im Baum auf u gesetzt.
                                if u in U:
                                    T[v] = u
                                    break
                        for u in L:
                            # Wenn die Kante (u, v) bereits Teil des aktuellen Matchings M ist, wird der Knoten u zum alternierenden Baum hinzugefügt,
                            # und sein Vorgänger wird auf v gesetzt.
                            if (u, v) in M:
                                U.add(u)
                                T[u] = v
                                break
                        # Augmentierender Pfad gefunden:
                        # Das bedeutet, dass ein neuer Knoten v gefunden wurde, der über eine Kante mit Slack-Wert 0 mit einem Knoten u in L verbunden ist,
                        # der noch nicht im alternierenden Baum U enthalten ist. Das heißt, dass möglicherweise ein augmentierenden Pfad gefunden wurde.
                        else:
                            # Der Pfad wird rückwärts durchlaufen, beginnend bei v, indem jeweils der Vorgängerknoten aus dem Dictionary T entnommen wird.
                            # Der Pfad wird in umgekehrter Reihenfolge in augmenting_path gespeichert.
                            augmenting_path: List[Tuple[int, int]] = []
                            current: int = v
                            while current is not None:
                                prev: int = T[current]
                                augmenting_path.append((prev, current))
                                current = T[prev]
                            found_augmenting_path = True
                            break

            if found_augmenting_path:
                # Wenn ein augmentierender Pfad (ein Pfad, der mit einem freien Knoten in L beginnt und mit einem freien Knoten in R endet,
                # wobei sich Matching-Kanten und Nicht-Matching-Kanten abwechseln) gefunden wird, wird das Matching entlang dieses Pfades augmentiert,
                # d.h., Matching-Kanten werden entfernt und Nicht-Matching-Kanten werden zum Matching hinzugefügt.
                for u, v in augmenting_path:
                    if (u, v) in M:
                        M.remove((u, v))
                    else:
                        M.add((u, v))
            else:
                # Überprüfung, ob die Nachbarn der nicht freien Knoten in U alle in U enthalten sind. Wenn dies der Fall ist,
                # bedeutet das laut dem Satz von Hall, dass kein perfektes Matching existiert.
                neighbors_set = set()
                neighbors_set = (neighbors_set.union(self.graph.neighbors(u)) for u in U & L)
                if all(n in U for n in neighbors_set):
                    return None
                break

        return M

def get_static_graph() -> Tuple[nx.Graph, Set[int]]:
    graph = nx.Graph()
    graph.add_nodes_from([1, 2, 3, 4], bipartite=0)
    graph.add_nodes_from([5, 6, 7, 8], bipartite=1)
    edges: List[Dict[str, int]] = [
        {'node1': 1, 'node2': 5, 'weight': 10},
        {'node1': 1, 'node2': 6, 'weight': 5},
        {'node1': 1, 'node2': 8, 'weight': 5},

        {'node1': 2, 'node2': 6, 'weight': 5},
        {'node1': 2, 'node2': 7, 'weight': 5},
        {'node1': 2, 'node2': 8, 'weight': 10},

        {'node1': 3, 'node2': 5, 'weight': 5},
        {'node1': 3, 'node2': 6, 'weight': 5},
        {'node1': 3, 'node2': 7, 'weight': 10},

        {'node1': 4, 'node2': 5, 'weight': 5},
        {'node1': 4, 'node2': 7, 'weight': 10},
        {'node1': 4, 'node2': 8, 'weight': 5}
    ]

    for edge in edges:
        graph.add_edge(edge['node1'], edge['node2'], weight=edge['weight'])

    left_set: Set[int] = {n for n, d in graph.nodes(data=True) if d['bipartite'] == 0}

    return graph, left_set

def get_random_graph() -> Tuple[nx.Graph, Set[int]]:
    graph: nx.Graph = bipartite.random_graph(4, 4, 0.8)

    for (u, v) in graph.edges():
        graph.edges[u, v]['weight'] = random.randint(1, 15)

    left_set: Set[int] = bipartite.sets(graph)[0]

    return graph, left_set

def main(graph_type: str = "random") -> None:
    graph, left_set = get_random_graph()
    if graph_type == "static":
        graph, left_set = get_static_graph()

    algorithm = Algorithm(graph)
    matching: Set[Tuple[int, int]] = algorithm.run()
    sorted_matching = {(min(u, v), max(u, v)) for u, v in matching}
    sorted_matching = sorted(sorted_matching, key=lambda x: x[0])
    print("Matching:", sorted_matching)

    nx_matching: Set[Tuple[int, int]] = nx.max_weight_matching(graph)
    sorted_nx_matching = {(min(u, v), max(u, v)) for u, v in nx_matching}
    sorted_nx_matching = sorted(sorted_nx_matching, key=lambda x: x[0])
    print("Matching:", sorted_nx_matching)

    pos = nx.drawing.layout.bipartite_layout(graph, left_set)
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Draw calculated matching
    nx.draw(graph, pos, with_labels=True, edge_color='black', ax=ax1)
    nx.draw_networkx_edges(graph, pos, edgelist=matching, edge_color='red', width=2, ax=ax1)
    edge_labels = {(u, v): graph[u][v]['weight'] for u, v in matching}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax1, label_pos=0.2)
    ax1.set_title("Calculated Matching")

    # Draw networkx matching
    nx.draw(graph, pos, with_labels=True, edge_color='black', ax=ax2)
    nx.draw_networkx_edges(graph, pos, edgelist=nx_matching, edge_color='red', width=2, ax=ax2)
    edge_labels = {(u, v): graph[u][v]['weight'] for u, v in nx_matching}
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, ax=ax2, label_pos=0.2)
    ax2.set_title("Networkx Matching")

    plt.show()

if __name__ == "__main__":
    main()
