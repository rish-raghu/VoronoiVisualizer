import math

def computeBisector(leftPt, rightPt):
    slope = -1/((leftPt[1] - rightPt[1])/(leftPt[0] - rightPt[0]))
    midpt = (leftPt + rightPt)/2
    yint = midpt[1] - slope * midpt[0]
    return slope, yint

def evalParabola(focus, directix, x):
    return 0.5/(focus[1]-directix)*(x-focus[0])**2 + (focus[1]+directix)/2

def computeBreakpoint(leftArc, rightArc, sweepline):     
    a1 = 0.5/(leftArc[1]-sweepline)
    b1 = (leftArc[1]+sweepline)/2
    a2 = 0.5/(rightArc[1]-sweepline)
    b2 = (rightArc[1]+sweepline)/2
    A = a1-a2
    B = 2*a2*rightArc[0] - 2*a1*leftArc[0]
    C = a1*leftArc[0]**2 - a2*rightArc[0]**2 + b1 - b2
    discrim = B**2 - 4*A*C
    if discrim < 0:
        raise ValueError
    elif discrim > 0:

        # compute possible breakpoints
        x1 = (-B + math.sqrt(discrim))/(2*A)
        x2 = (-B - math.sqrt(discrim))/(2*A)

        # check which solution is correct
        yRightArcLeft = evalParabola(leftArc, sweepline, x1+0.1)
        yRightArcRight = evalParabola(rightArc, sweepline, x1+0.1)
        if yRightArcRight < yRightArcLeft:
            return x1
        else:
            return x2
    else:
        return -B/(2*A)

def CCW(A, B, C):
    # x1(y2-y3) - x2(y1-y3) + x3(y1-y2)
    det = A[0]*(B[1]-C[1]) - B[0]*(A[1]-C[1]) + C[0]*(A[1]-B[1])
    if not (A == B).all():
        if det < 0: # clockwise
            return 1
        elif det  > 0:
            return -1
        else:
            if min(A[0], B[0]) <= C[0] <= max(A[0], B[0]) and min(A[1], B[1]) <= C[1] <= max(A[1], B[1]):
                return 0
            elif min(A[0], C[0]) <= B[0] <= max(A[0], C[0]) and min(A[1], C[1]) <= B[1] <= max(A[1], C[1]):
                return 2
            else:
                return -2
    else:
        if A == C:
            return 0
        else:
            return 2
            