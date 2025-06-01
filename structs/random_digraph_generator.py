import random
import networkx as nx

from itertools import combinations 

class GenerateRandomDigraph: 
    def __init__(self, n: int, p: int) -> None: 
        self.n: int = n 
        self.p: int = p 
        self.graph: nx.DiGraph = None 
 
    def generate(self) -> nx.DiGraph: 
        self.graph = nx.DiGraph() 
 
        if self.p > 100 or self.p < 0: 
            return self.graph 
 
        for node1, node2 in combinations(range(self.n), 2): 
            if random.randint(0, 100) < self.p: 
                self.graph.add_edge(node1, node2, capacity=random.randint(4,20)) 
        return self.graph 
