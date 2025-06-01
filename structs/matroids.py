import networkx as nx

from abc import ABC, abstractmethod
from typing import Set, Tuple, List
from structs.union_find import UnionFind

class Matroid(ABC):
    def __init__(self, groundset: Set) -> None:
        self.groundset: Set = groundset

    @abstractmethod
    def minarg(self, U):
        pass

    @abstractmethod
    def independent(self, U) -> bool:
        pass

    @abstractmethod
    def rank(self, U) -> int:
        pass

class GraphMatroid(Matroid):
    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph.copy()
        super().__init__({e: data['weight'] for e, data in graph.edges.items()})
        self.union_find = UnionFind(list(graph.nodes()))

    def minarg(self, U: Set) -> Set:
        return min(U, key=lambda x: self.groundset[x])

    def independent(self, U: Set) -> bool:
        temp_union_find = self.union_find.copy()
        for u, v in U:
            if temp_union_find.find(u) == temp_union_find.find(v):
                return False
            temp_union_find.union(u, v)
        return True
    
    def rank(self, U: Set) -> int:
        rank: int = 0
        temp_union_find = self.union_find.copy()
        for u, v in U:
            if temp_union_find.find(u) != temp_union_find.find(v):
                temp_union_find.union(u, v)
                rank += 1
        return rank

class UnweightedGraphMatroid(Matroid):
    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph.copy()
        self.union_find = UnionFind(list(graph.nodes()))

    def minarg(self, U: Set) -> Tuple:
        return min(U, key=lambda edge: nx.shortest_path_length(self.graph, *edge))

    def independent(self, U: Set) -> bool:
        temp_union_find = self.union_find.copy()
        for edge in U:
            if isinstance(edge, tuple) and len(edge) == 2:
                u, v = edge
                if temp_union_find.find(u) == temp_union_find.find(v):
                    return False
                temp_union_find.union(u, v)
        return True

    def rank(self, U: Set) -> int:
        return sum(1 for u, v in U if self.union_find.find(u) != self.union_find.find(v))

    def edges(self) -> Set:
        return set(self.graph.edges())

class PartitionMatroid(Matroid):
    def __init__(self, partitions: List[Set]) -> None:
        self.partitions = partitions
        self.element_to_partition = {}
        for i, partition in enumerate(partitions):
            for element in partition:
                self.element_to_partition[element] = i

    def minarg(self, U):
        return super().minarg(U)

    def independent(self, U: Set) -> bool:
        partition_counts = [0] * len(self.partitions)
        for element in U:
            partition_index = self.element_to_partition.get(element)
            if partition_index is not None:
                partition_counts[partition_index] += 1
                if partition_counts[partition_index] > 1:
                    return False
        return True

    def rank(self, U: Set) -> int:
        unique_partitions = set()
        for element in U:
            partition_index = self.element_to_partition.get(element)
            if partition_index is not None:
                unique_partitions.add(partition_index)
        return len(unique_partitions)

    def edges(self) -> Set:
        return set.union(*self.partitions)
