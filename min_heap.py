import heapq

class FixedSizeMaxKeeper:
    def __init__(self, max_size=5):
        self.heap = []
        self.max_size = max_size

    def push(self, item):
        if len(self.heap) < self.max_size:
            heapq.heappush(self.heap, item)
        else:
            if item > self.heap[0]:
                heapq.heapreplace(self.heap, item)

    def get_items(self):
        return sorted(self.heap)

# test
pq = FixedSizeMaxKeeper(5)
data = [(10, 100), (5, 200), (8, 300), (3, 400), (7, 500), (1, 600), (6, 700), (12, 800)]

for elem in data:
    pq.push(elem)

print(pq.get_items())
