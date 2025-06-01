from typing import List, Tuple

class PriorityQueue:
    def __init__(self) -> None:
        self.heap: List[Tuple[int, int]] = []

    # Fügt ein Element mit einer bestimmten Priorität zur Warteschlange hinzu.
    def push(self, item: int, priotity: int) -> None:
        # Fügt das Element als Tupel (Priorität, Element) zum Heap hinzu.
        self.heap.append((priotity, item))
        # Stellt die Heap-Eigenschaft von unten nach oben wieder her.
        self._heapify_up(len(self.heap) - 1)

    # Entfernt und gibt das Element mit der höchsten Priorität (niedrigster Wert) zurück.
    def pop(self) -> int:
        # Entfernt das erste Element aus dem Heap und gibt es zurück.
        return self.heap.pop(0)[1]
    
    def empty(self) -> bool:
        return len(self.heap) == 0
    
    # Stellt die Heap-Eigenschaft von einem gegebenen Index aus nach oben wieder her.
    def _heapify_up(self, i: int) -> None:
        # Berechnet den Index des Elternelements.
        parent: int = (i - 1) // 2
        # Überprüft, ob das aktuelle Element eine höhere Priorität als sein Elternteil hat.
        if parent >= 0 and self.heap[i][0] < self.heap[parent][0]:
            # Tauscht das aktuelle Element mit seinem Elternteil.
            self._swap(i, parent)
            # Wiederholt den Prozess rekursiv für das Elternteil.
            self._heapify_up(parent)

    def _swap(self, i: int, j: int):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
