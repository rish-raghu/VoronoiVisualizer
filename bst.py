# Implements binary search tree
import utils

class Leaf:
        def __init__(self, site):
            self.site = site
            self.parent = None
            self.event = None # arc disappearance event

        def __str__(self):
            return str(self.site)

class Internal:
    def __init__(self, leftSite, rightSite):
        self.leftSite = leftSite
        self.rightSite = rightSite
        self.leftNode = None
        self.rightNode = None
        self.parent = None
        self.halfEdge = None

    def __str__(self):
        return str(self.leftSite) + " " + str(self.rightSite)

class BST:

    def __init__(self):
        self.root = None

    def _findLeftLeaf(self, leaf):
            currNode = leaf
            if currNode == self.root: return None
            child = currNode
            currNode = currNode.parent
            while currNode.leftNode is child:
                if currNode == self.root: return None
                child = currNode
                currNode = currNode.parent

            currNode = currNode.leftNode
            while isinstance(currNode, Internal):
                currNode = currNode.rightNode
            
            return currNode

    def _findRightLeaf(self, leaf):
        currNode = leaf 
        if currNode is self.root: return None
        child = currNode
        currNode = currNode.parent
        while currNode.rightNode is child:
            if currNode is self.root: return None
            child = currNode
            currNode = currNode.parent
            
        currNode = currNode.rightNode
        while isinstance(currNode, Internal):
            currNode = currNode.leftNode

        return currNode


    def insertSite(self, newSite, sweepline):

        if not self.root:
            self.root = Leaf(newSite)
            return None

        # Find arc directly above newSite
        currNode = self.root
        while True:
            if isinstance(currNode, Leaf):
                break
            breakpointX = utils.computeBreakpoint(currNode.leftSite, currNode.rightSite, sweepline)
            if newSite[0] < breakpointX:
                currNode = currNode.leftNode
            elif newSite[0] > breakpointX:
                currNode = currNode.rightNode
            else:
                raise NotImplementedError
        
        # Split arc with newSite
        oldSite = currNode.site
        topInternal = Internal(newSite, oldSite)
        if currNode.parent:
            if currNode.parent.leftNode is currNode:
                currNode.parent.leftNode = topInternal
            else:
                currNode.parent.rightNode = topInternal
            topInternal.parent = currNode.parent
        else:
            self.root = topInternal
        rightLeaf = Leaf(oldSite)
        topInternal.rightNode = rightLeaf
        rightLeaf.parent = topInternal
        leftInternal = Internal(oldSite, newSite)
        topInternal.leftNode = leftInternal
        leftInternal.parent = topInternal
        leftLeaf = Leaf(oldSite)
        leftInternal.leftNode = leftLeaf
        leftLeaf.parent = leftInternal
        midLeaf = Leaf(newSite)
        leftInternal.rightNode = midLeaf
        midLeaf.parent = leftInternal

        # Find circle events
        leftTripletLeftLeaf = self._findLeftLeaf(leftLeaf) # find leftmost arc leaf for triplet with newSite as rightmost arc
        rightTripletRightLeaf = self._findRightLeaf(rightLeaf) # find rightmost arc leaf for triplet with newSite as leftmost arc 

        return {
            'splitLeaf': currNode,
            'midLeaf': midLeaf,
            'leftLeaf': leftLeaf,
            'rightLeaf': rightLeaf,
            'leftTripletLeftLeaf': leftTripletLeftLeaf,
            'rightTripletRightLeaf': rightTripletRightLeaf,
            'rightInternal': topInternal,
            'leftInternal': leftInternal
        }

    def deleteSite(self, delLeaf):

        # Get left and right adjacent leaves to deletion leaf
        leftLeaf = self._findLeftLeaf(delLeaf)
        rightLeaf = self._findRightLeaf(delLeaf)

        # remove leaf and its parent internal node
        oldRightInternal, oldLeftInternal = None, None
        if delLeaf.parent.leftNode is delLeaf:
            adjSite = delLeaf.parent.rightSite
            siblingNode = delLeaf.parent.rightNode
            oldRightInternal = delLeaf.parent
            
            # reattach other child of parent internal node
            if delLeaf.parent.parent.leftNode is delLeaf.parent:
                delLeaf.parent.parent.leftNode = siblingNode
            else:
                delLeaf.parent.parent.rightNode = siblingNode
            siblingNode.parent = delLeaf.parent.parent

            currNode = leftLeaf.parent
            while not ((currNode.leftSite == leftLeaf.site).all() and (currNode.rightSite == delLeaf.site).all()):
                currNode = currNode.parent
            
            newNode = Internal(currNode.leftSite, adjSite)
            newNode.leftNode = currNode.leftNode
            newNode.leftNode.parent = newNode
            newNode.rightNode = currNode.rightNode
            newNode.rightNode.parent = newNode
            if currNode is self.root:
                self.root = newNode
            else:
                newNode.parent = currNode.parent
                if newNode.parent.leftNode is currNode:
                    newNode.parent.leftNode = newNode
                else:
                    newNode.parent.rightNode = newNode

            oldLeftInternal = currNode
        else:
            adjSite = delLeaf.parent.leftSite
            siblingNode = delLeaf.parent.leftNode
            oldLeftInternal = delLeaf.parent

            # reattach other child of parent internal node
            if delLeaf.parent.parent.leftNode is delLeaf.parent:
                delLeaf.parent.parent.leftNode = siblingNode
            else:
                delLeaf.parent.parent.rightNode = siblingNode
            siblingNode.parent = delLeaf.parent.parent

            currNode = rightLeaf.parent
            while not ((currNode.rightSite == rightLeaf.site).all() and (currNode.leftSite == delLeaf.site).all()):
                currNode = currNode.parent

            newNode = Internal(adjSite, currNode.rightSite)
            newNode.leftNode = currNode.leftNode
            newNode.leftNode.parent = newNode
            newNode.rightNode = currNode.rightNode
            newNode.rightNode.parent = newNode
            if currNode is self.root:
                self.root = newNode
            else:
                newNode.parent = currNode.parent
                if newNode.parent.leftNode is currNode:
                    newNode.parent.leftNode = newNode
                else:
                    newNode.parent.rightNode = newNode

            oldRightInternal = currNode

        # Get leftmost and rightmost leaves of two new triplets
        leftTripletLeftLeaf = self._findLeftLeaf(leftLeaf)
        rightTripletRightLeaf = self._findRightLeaf(rightLeaf)

        return {
            'leftLeaf': leftLeaf,
            'rightLeaf': rightLeaf,
            'leftTripletLeftLeaf': leftTripletLeftLeaf,
            'rightTripletRightLeaf': rightTripletRightLeaf,
            'oldLeftInternal': oldLeftInternal,
            'oldRightInternal': oldRightInternal,
            'newInternal': newNode
        }

    def isEmpty(self):
        return not bool(self.root)

    def inorderTraversal(self):
        def inorderTraversalHelper(root, level):
            
            if isinstance(root, Internal):
                inorderTraversalHelper(root.leftNode, level+1)
                print("Internal", root.leftSite, root.rightSite, level)
                inorderTraversalHelper(root.rightNode, level+1)
            else:
                print("Leaf", root.site, level)
        
        inorderTraversalHelper(self.root, 1)

    def getInternals(self):
        internals = []

        def inorderTraversalHelper(root):
            if isinstance(root, Internal):
                inorderTraversalHelper(root.leftNode)
                internals.append(root)
                inorderTraversalHelper(root.rightNode)

        inorderTraversalHelper(self.root)
        return internals
       