# Implements doubly connected edge list

class DCEL:
    class HalfEdge:
        def __init__(self):
            self.twin = None
            self.origin = None
            self.next = None
            self.prev = None
            self.face = None
            self.internal = None # for debugging
            # is vertical line that travels infinitely in the positive y direction
            self.topVertical = False 

    class Vertex:
        def __init__(self):
            self.coords = None
            self.edge = None

    class Face:
        def __init__(self):
            self.edge = None

    def __init__(self):
        self.halfEdges = []
        self.vertices = []
        self.faces = []

    def newHalfEdge(self):
        halfEdge = self.HalfEdge()
        self.halfEdges.append(halfEdge)
        return halfEdge

    def newVertex(self):
        vertex = self.Vertex()
        self.vertices.append(vertex)
        return vertex

    def newFace(self):
        face = self.Face()
        self.faces.append(face)
        return face

    def __str__(self):
        res = ""
        for halfEdge in self.halfEdges:
            res = res + str(halfEdge.origin.coords) if halfEdge.origin else res + "none"
            res += " "
            res = res + str(halfEdge.twin.origin.coords) if halfEdge.twin.origin else res + "none"
            res += " "
            res += str(halfEdge.internal.leftSite) + " " + str(halfEdge.internal.rightSite)
            res += "\n"
        return res
    