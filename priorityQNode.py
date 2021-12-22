# Defines a node for representing events in priority queue

class QNode:
    def __init__(self, point, sweepline, arc=None):
        self.point = point
        self.arc = arc
        self.toRemove = False
        self.sweepline = sweepline

    def __lt__(self, other):
        return self.sweepline > other.sweepline
