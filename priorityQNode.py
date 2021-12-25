# Defines a node for representing events in priority queue
import math

class QNode:
    def __init__(self, point, sweepline, arc=None):
        self.point = point
        self.arc = arc
        self.toRemove = False
        self.sweepline = sweepline

    def __lt__(self, other):
        if math.isclose(self.sweepline, other.sweepline):
            return self.point[0] < other.point[0]
        return self.sweepline > other.sweepline
