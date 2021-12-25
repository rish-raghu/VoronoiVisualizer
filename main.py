import heapq
from dcel import DCEL
from priorityQNode import QNode
from bst import BST
import utils
from types import SimpleNamespace
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import argparse
import math

#np.random.seed(0)
mpl.use('tkagg')

def computeVoronoi(points, debug=False):

    def _computeCircleEvent(leftLeaf, midLeaf, rightLeaf):
        
        if utils.CCW(leftLeaf.site, midLeaf.site, rightLeaf.site) > 0:
            slopeLeft, yintLeft = utils.computeBisector(leftLeaf.site, midLeaf.site)
            slopeRight, yintRight = utils.computeBisector(midLeaf.site, rightLeaf.site)

            if math.isclose(slopeLeft, slopeRight):
                return None, None
            
            if slopeLeft==float('inf'):
                intersectX = yintLeft
                intersectY = slopeRight * intersectX + yintRight
            elif slopeRight==float('inf'):
                intersectX = yintRight
                intersectY = slopeLeft * intersectX + yintLeft
            else:
                intersectX = (yintRight - yintLeft)/(slopeLeft - slopeRight)
                intersectY = slopeLeft * intersectX + yintLeft
            
            radius = np.sqrt(np.sum((leftLeaf.site - np.array([intersectX, intersectY]))**2))
            sweepline = intersectY - radius
            
            return (intersectX, intersectY), sweepline
        else:
            return None, None


    def _handleCircleEvent(event):
        delLeaf = event.arc

        # Delete leaf of T representing disappearing arc
        n = T.deleteSite(delLeaf)
        n = SimpleNamespace(**n)

        # Delete circle events involving arc
        if n.leftLeaf.event:
            n.leftLeaf.event.toRemove = True
        if n.rightLeaf.event:
            n.rightLeaf.event.toRemove = True

        # Create new vertex and half-edge records
        vertex = D.newVertex()
        edgeOut, edgeIn = D.newHalfEdge(), D.newHalfEdge()
        edgeOut.twin = edgeIn
        edgeIn.twin = edgeOut
        edgeOut.origin = vertex
        vertex.edge = edgeOut
        vertex.coords = event.point
        n.newInternal.halfEdge = edgeOut

        if not n.oldLeftInternal.halfEdge.origin:
            n.oldLeftInternal.halfEdge.origin = vertex
            n.oldLeftInternal.halfEdge.prev = edgeIn
            edgeIn.next = n.oldLeftInternal.halfEdge
            leftIn = n.oldLeftInternal.halfEdge.twin
        else:
            n.oldLeftInternal.halfEdge.twin.origin = vertex
            n.oldLeftInternal.halfEdge.twin.prev = edgeIn
            edgeIn.next = n.oldLeftInternal.halfEdge.twin
            leftIn = n.oldLeftInternal.halfEdge

        if not n.oldRightInternal.halfEdge.origin:
            n.oldRightInternal.halfEdge.origin = vertex
            n.oldRightInternal.halfEdge.twin.next = edgeOut
            edgeOut.prev = n.oldRightInternal.halfEdge.twin
            rightOut = n.oldRightInternal.halfEdge
        else:
            n.oldRightInternal.halfEdge.twin.origin = vertex
            n.oldRightInternal.halfEdge.next = edgeOut
            edgeOut.prev = n.oldRightInternal.halfEdge
            rightOut = n.oldRightInternal.halfEdge.twin

        leftIn.next = rightOut
        rightOut.prev = leftIn

        # Compute future circle events
        if n.leftTripletLeftLeaf and n.leftLeaf and n.rightLeaf:
            intersectLeft, sweeplineLeft = _computeCircleEvent(n.leftTripletLeftLeaf, n.leftLeaf, n.rightLeaf)
            if intersectLeft:
                newCircleEvent = QNode(intersectLeft, sweeplineLeft, arc=n.leftLeaf)
                heapq.heappush(Q, newCircleEvent)
                n.leftLeaf.event = newCircleEvent
        if n.leftLeaf and n.rightLeaf and n.rightTripletRightLeaf:
            intersectRight, sweeplineRight = _computeCircleEvent(n.leftLeaf, n.rightLeaf, n.rightTripletRightLeaf)
            if intersectRight:
                newCircleEvent = QNode(intersectRight, sweeplineRight, arc=n.rightLeaf)
                heapq.heappush(Q, newCircleEvent)
                n.rightLeaf.event = newCircleEvent


    def _handleSiteEvent(event, isFirstSweepline=False):
        site = event.point

        # Find arc above site and add site
        if T.isEmpty():
            T.insertSite(site, event.sweepline) 
            return

        n = T.insertSite(site, event.sweepline, isFirstSweepline=isFirstSweepline) 
        n = SimpleNamespace(**n)

        # Create new half-edge records
        edge1, edge2 = D.newHalfEdge(), D.newHalfEdge()
        edge1.twin = edge2
        edge2.twin = edge1
        
        if isFirstSweepline:
            edge1.topVertical = True
            edge2.topVertical = True
            n.newInternal.halfEdge = edge1
            return

        n.leftInternal.halfEdge = edge1
        n.rightInternal.halfEdge = edge1
        
        # Circle event of found arc is a false alarm
        if n.splitLeaf.event:
            n.splitLeaf.event.toRemove = True

        # Compute future circle events
        if n.leftTripletLeftLeaf and n.leftLeaf and n.midLeaf:
            intersectLeft, sweeplineLeft = _computeCircleEvent(n.leftTripletLeftLeaf, n.leftLeaf, n.midLeaf)
            if intersectLeft:
                newCircleEvent = QNode(intersectLeft, sweeplineLeft, arc=n.leftLeaf)
                heapq.heappush(Q, newCircleEvent)
                n.leftLeaf.event = newCircleEvent
        if n.midLeaf and n.rightLeaf and n.rightTripletRightLeaf:
            intersectRight, sweeplineRight = _computeCircleEvent(n.midLeaf, n.rightLeaf, n.rightTripletRightLeaf)
            if intersectRight:
                newCircleEvent = QNode(intersectRight, sweeplineRight, arc=n.rightLeaf)
                heapq.heappush(Q, newCircleEvent)
                n.rightLeaf.event = newCircleEvent


    # Initialize event queue Q with all site events, empty status structure T, and empty DCEL D
    Q = []
    for point in points:
        heapq.heappush(Q, QNode(point, point[1]))
    T = BST()
    D = DCEL()

    # Process events
    numEvents = 0
    while Q:
        event = heapq.heappop(Q)
        if event.toRemove: continue

        if event.arc:
            _handleCircleEvent(event)
        else:
            if numEvents==0:
                firstSweepline = event.point[1]
            # when the highest y-coordinate is shared by multiple sites, we have a special case
            if math.isclose(event.point[1], firstSweepline):
                _handleSiteEvent(event, isFirstSweepline=True)
            else:
                _handleSiteEvent(event)

        numEvents += 1

        if debug:
            print("Event", event.point)
            print("\nTree:")
            T.inorderTraversal()
            print("\nEvent queue:")
            print([e.point for e in list(Q)])
            print("--------------------------")

    return D, T, event.sweepline


def displayVoronoi(points, D, T, sweepline):
    plt.scatter([pt[0] for pt in points], [pt[1] for pt in points], c='b')
    plt.scatter([v.coords[0] for v in D.vertices], [v.coords[1] for v in D.vertices], c='r')

    bottomBound, topBound = float('inf'), float('-inf')
    leftBound, rightBound = float('inf'), float('-inf')
    for v in D.vertices:
        bottomBound = min(bottomBound, v.coords[1])
        topBound = max(topBound, v.coords[1])
        leftBound = min(leftBound, v.coords[0])
        rightBound = max(rightBound, v.coords[0])
    for pt in points:
        bottomBound = min(bottomBound, pt[1])
        topBound = max(topBound, pt[1])
        leftBound = min(leftBound, pt[0])
        rightBound = max(rightBound, pt[0])
    bottomBound -= 1
    topBound += 1
    leftBound -= 1
    rightBound += 1

    plt.plot([leftBound, rightBound], [topBound, topBound], c='black')
    plt.plot([leftBound, rightBound], [bottomBound, bottomBound], c='black')
    plt.plot([leftBound, leftBound], [bottomBound, topBound], c='black')
    plt.plot([rightBound, rightBound], [bottomBound, topBound], c='black')

    for halfEdge in D.halfEdges:
        if halfEdge.topVertical and halfEdge.origin:
                plt.plot([halfEdge.origin.coords[0], halfEdge.origin.coords[0]], [halfEdge.origin.coords[1], topBound], c='orange')
        elif halfEdge.topVertical and halfEdge.twin.origin:
                plt.plot([halfEdge.twin.origin.coords[0], halfEdge.twin.origin.coords[0]], [halfEdge.twin.origin.coords[1], topBound], c='orange')
        elif halfEdge.origin and halfEdge.twin.origin:
            plt.plot([halfEdge.origin.coords[0], halfEdge.twin.origin.coords[0]], [halfEdge.origin.coords[1], halfEdge.twin.origin.coords[1]], c='orange')
    
    internalNodes = T.getInternals()
    for node in internalNodes:
        slope, yint = utils.computeBisector(node.leftSite, node.rightSite)
        if not (node.halfEdge.origin or node.halfEdge.twin.origin):
            if slope==float('inf'):
                plt.plot([yint, yint], [bottomBound, topBound], c='orange')
            elif math.isclose(slope, 0):
                plt.plot([leftBound, rightBound], [yint, yint], c='orange')
            else:
                endptXs, endptYs = [], []
                intXBottom = (bottomBound - yint)/slope
                intXTop = (topBound - yint)/slope
                intYLeft = slope*leftBound+yint
                intYRight = slope*rightBound+yint
                if leftBound <= intXBottom <= rightBound:
                    endptXs.append(intXBottom)
                    endptYs.append(bottomBound)
                if leftBound <= intXTop <= rightBound:
                    endptXs.append(intXTop)
                    endptYs.append(topBound)
                if bottomBound <= intYLeft <= topBound:
                    endptXs.append(leftBound)
                    endptYs.append(intYLeft)
                if bottomBound <= intYRight <= topBound:
                    endptXs.append(rightBound)
                    endptYs.append(intYRight)
                plt.plot(endptXs, endptYs, c='orange')
        else:
            endpt = node.halfEdge.origin.coords if node.halfEdge.origin else node.halfEdge.twin.origin.coords
            breakpoint = utils.computeBreakpoint(node.leftSite, node.rightSite, sweepline-1)
            
            if slope==float('inf'):
                if breakpoint[1] > endpt[1]:
                    plt.plot([endpt[0], endpt[0]], [endpt[1], topBound], c='orange')
                else:
                    plt.plot([endpt[0], endpt[0]], [endpt[1], bottomBound], c='orange')
            elif math.isclose(slope, 0):
                if breakpoint[0] > endpt[0]:
                    plt.plot([endpt[0], rightBound], [endpt[1], endpt[1]], c='orange')
                else:
                    plt.plot([endpt[0], leftBound], [endpt[1], endpt[1]], c='orange')
            else:
                intXBottom = (bottomBound - yint)/slope
                intXTop = (topBound - yint)/slope
                intYLeft = slope*leftBound+yint
                intYRight = slope*rightBound+yint
                if leftBound <= intXBottom <= rightBound and ((breakpoint[0] > endpt[0] and intXBottom > endpt[0]) or (breakpoint[0] < endpt[0] and intXBottom < endpt[0])):
                    plt.plot([endpt[0], intXBottom], [endpt[1], bottomBound], c='orange')
                elif leftBound <= intXTop <= rightBound and ((breakpoint[0] > endpt[0] and intXTop > endpt[0]) or (breakpoint[0] < endpt[0] and intXTop < endpt[0])):
                    plt.plot([endpt[0], intXTop], [endpt[1], topBound], c='orange')
                elif bottomBound <= intYLeft <= topBound and breakpoint[0] < endpt[0]:
                    plt.plot([endpt[0], leftBound], [endpt[1], intYLeft], c='orange')
                elif bottomBound <= intYRight <= topBound and breakpoint[0] > endpt[0]:
                    plt.plot([endpt[0], rightBound], [endpt[1], intYRight], c='orange')

    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Visualize Voronoi diagram of set of points")
    parser.add_argument('num_pts', metavar='N', type=int, help="Number of points to generate")
    parser.add_argument('--debug', action='store_true', help="Print tree and queue at each event")
    args = parser.parse_args()

    scale = 10
    #points = scale * np.random.rand(args.num_pts, 2)
    #points[args.num_pts//2:, 0] = points[:args.num_pts//2, 0] # horizontal edges test
    #points[args.num_pts//2:, 1] = points[:args.num_pts//2, 1] # vertical edges test
    #points = np.array([[3, 3], [4, 7], [5, 3]])
    points = np.array([[1, 5], [2, 5], [4, 5], [0, 3], [3.5, 3], [0, 1], [3, 1]])
    D, T, sweepline = computeVoronoi(points, debug=args.debug)
    displayVoronoi(points, D, T, sweepline)
