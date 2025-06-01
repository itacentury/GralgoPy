from typing import List, Dict

class UnionFind:
    def __init__(self, elements: List) -> None:
        self.parent: Dict[int, int] = {element: element for element in elements}
        # Initialisiert die Rangliste aller Knoten mit 0.
        self.rank: Dict[int, int] = {element: 0 for element in elements}

    # Findet den Wurzelknoten eines Elements mit Pfadkompression.
    def find(self, x: int) -> int:
        # Wenn x nicht sein eigener Elternteil ist, finde seinen Elternteil.
        if self.parent[x] != x:
            # Pfadkompression:  Verbinde x direkt mit seinem Wurzelknoten.
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    # Vereinigt zwei Mengen basierend auf den Rängen ihrer Wurzeln.
    def union(self, x: int, y: int) -> None:
        # Findet die Wurzelknoten von x und y.
        root_x: int = self.find(x)
        root_y: int = self.find(y)

        # Wenn die Wurzeln unterschiedlich sind, müssen die Bäume vereinigt werden.
        if root_x != root_y:
            # Vereinigt die Bäume basierend auf ihren Rängen.
            if self.rank[root_x] < self.rank[root_y]:
                # Wenn der Rang von root_x kleiner ist, wird root_y zum Elternteil von root_x.
                self.parent[root_x] = root_y
            elif self.rank[root_x] > self.rank[root_y]:
                # Wenn der Rang von root_y kleiner ist, wird root_x zum Elternteil von root_y.
                self.parent[root_y] = root_x
            else:
                # Wenn die Ränge gleich sind, wähle einen als Elternteil und erhöhe seinen Rang um 1.
                self.parent[root_y] = root_x
                self.rank[root_x] += 1

    def copy(self) -> "UnionFind":
        new_instance = UnionFind(list(self.parent.keys()))
        new_instance.parent = self.parent.copy()
        new_instance.rank = self.rank.copy()
        return new_instance