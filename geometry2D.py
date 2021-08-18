from sympy import *
from sympy.geometry import *

import math


class Point:
    """A point identified by (x,y) coordinates.
    
    supports: +, -, *, /, str, repr
    
    length  -- calculate length of vector to point from origin
    distance_to  -- calculate distance between two points
    as_tuple  -- construct tuple (x,y)
    clone  -- construct a duplicate
    integerize  -- convert x & y to integers
    floatize  -- convert x & y to floats
    move_to  -- reset x & y
    slide  -- move (in place) +dx, +dy, as spec'd by point
    slide_xy  -- move (in place) +dx, +dy
    rotate  -- rotate around the origin
    rotate_about  -- rotate around another point
    """
    
    UNDEFINED = Point(-999999,-999999)  #returned, e.g., when looking for the intersection of two 
    
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        
    def toJSON(self):
        return "{\"x\": " + str(self.x) + ", \"y\": " + str(self.y) + "}"
    
    def __add__(self, p):
        """Point(x1+x2, y1+y2)"""
        return Point(self.x+p.x, self.y+p.y)
    
    def __sub__(self, p):
        """Point(x1-x2, y1-y2)"""
        return Point(self.x-p.x, self.y-p.y)
    
    def __mul__( self, scalar ):
        """Point(x1*x2, y1*y2)"""
        return Point(self.x*scalar, self.y*scalar)
    
    def __div__(self, scalar):
        """Point(x1/x2, y1/y2)"""
        return Point(self.x/scalar, self.y/scalar)
    
    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)
    
    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def distance_to(self, p):
        """Calculate the distance between two points."""
        return (self - p).length()
    
    def as_tuple(self):
        """(x, y)"""
        return (self.x, self.y)
    
    def clone(self):
        """Return a full copy of this point."""
        return Point(self.x, self.y)
    
    def integerize(self):
        """Convert co-ordinate values to integers."""
        self.x = int(self.x)
        self.y = int(self.y)
    
    def floatize(self):
        """Convert co-ordinate values to floats."""
        self.x = float(self.x)
        self.y = float(self.y)
    
    def move_to(self, x, y):
        """Reset x & y coordinates."""
        self.x = x
        self.y = y
    
    def slide(self, p):
        '''Move to new (x+dx,y+dy).
        
        Can anyone think up a better name for this function?
        slide? shift? delta? move_by?
        '''
        self.x = self.x + p.x
        self.y = self.y + p.y
    
    def slide_xy(self, dx, dy):
        '''Move to new (x+dx,y+dy).
        
        Can anyone think up a better name for this function?
        slide? shift? delta? move_by?
        '''
        self.x = self.x + dx
        self.y = self.y + dy
    
    def rotate(self, rad):
        """Rotate counter-clockwise by rad radians.
        
        Positive y goes *up,* as in traditional mathematics.
        
        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.
        
        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c*self.x - s*self.y, s*self.x + c*self.y)
        return Point(x,y)
    
    def rotate_about(self, p, theta):
        """Rotate counter-clockwise around a point, by theta degrees.
        
        Positive y goes *up,* as in traditional mathematics.
        
        The new position is returned as a new Point.
        """
        result = self.clone()
        result.slide(-p.x, -p.y)
        result.rotate(theta)
        result.slide(p.x, p.y)
        return result
    
    def line_through_point(self, pt):
        if self.x != pt.x:
            m = (pt.y - self.y)/(pt.x - self.x)
            return Line(self, m)
        else:
            return Line(self, 0, inf_slope=True)
        
    def scaleToTurtleCanvas(self, boundingRect):
        boundingRectWidth = boundingRect.right - boundingRect.left
        boundingRectHeight = boundingRect.bottom - boundingRect.top
        scaled_x = (self.x / boundingRectWidth)*700 - 350
        scaled_y = (self.y / boundingRectHeight)*700 - 350

        return Point(scaled_x, scaled_y)
        
    def draw_circle_centered_at(self, turtle, radius, boundingRect, filled=False, color="black"):
        #get scaled location and draw there
        scaledPt = self.scaleToTurtleCanvas(boundingRect)
        turtle.penup()
        turtle.goto(scaledPt.x, scaledPt.y)
        turtle.pendown()
        if filled:
            turtle.color(color)
            turtle.dot(radius)
            turtle.color("black")
        else:
            turtle.circle(radius, color) 
            turtle.color("black")
        turtle.penup() 
        
class Line:    
    def __init__(self, pt, m, inf_slope=False):
        self.has_infinite_slope = inf_slope
        if inf_slope:
            self.const_x = pt.x
        else:
            self.slope = m
            self.y_intercept = pt.y - m * (pt.x)
                    
    
    def intersectionWithLine(self, line):
        if self.has_infinite_slope:  
            if line.has_infinite_slope:
                if self.const_x != line.const_x:
                    return Point.UNDEFINED
                else:
                    return Point(self.const_x, 0)
            else:
                return Point(self.const_x, line.slope * self.const_x + line.y_intercept)
        elif line.has_infinite_slope:
                return Point(line.const_y, self.slop * line.const_x + self.y_intercept)
        else:  
            if self.slope != line.slope:
                x = (self.y_intercept - line.y_intercept) / (line.slope - self.slope)
                y = self.slope * x + self.y_intercept
                return Point(x,y)
            else:
                if self.const_x != line.const_x:
                    return Point.UNDEFINED
                else:
                    return Point(self.const_x, 0)
        
class Segment:
    COLINEAR = -1
    CLOCKWISE = -2
    COUNTERCLOCKWISE = -3
    
    
    def __init__(self, pt1, pt2):
        """Initialize a segment from two points."""
        self.set_points(pt1, pt2)

    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        (self.x1, self.y1) = pt1.as_tuple()
        (self.x2, self.y2) = pt2.as_tuple()
        #self.left = min(x1, x2)
        #self.top = min(y1, y2)
        #self.right = max(x1, x2)
        #self.bottom = max(y1, y2)
        
    def toJSON(self):
        pt1 = Point(self.x1, self.y1)
        pt2 = Point(self.x2, self.y2)
        return "{\"pt1\": " + pt1.toJSON() + ", \"pt2\": " + pt2.toJSON() + "}"
        
    def endpoints(self):
        return [Point(self.x1, self.y1), Point(self.x2, self.y2)]
        
    def scaleToTurtleCanvas(self, boundingRect):  
        boundingRectWidth = boundingRect.right - boundingRect.left
        boundingRectHeight = boundingRect.bottom - boundingRect.top
        
        turtle_x1 = (self.x1 / boundingRectWidth)*700 - 350
        turtle_y1 = (self.y1 / boundingRectHeight)*700 -350
        turtle_x2 = (self.x2 / boundingRectWidth)*700 - 350
        turtle_y2 = (self.y2 / boundingRectHeight)*700 -350
        
        t1 = Point(turtle_x1, turtle_y1)
        t2 = Point(turtle_x2, turtle_y2)
        return Segment(t1, t2)
    
    def length(self):
        return math.sqrt((self.x2 - self.x1)*(self.x2 - self.x1) + (self.y2 - self.y1)*(self.y2 - self.y1))
        
    def midpoint(self):
        mid_x = (self.x1 + self.x2) /2.0
        mid_y = (self.y1 + self.y2) /2.0
        return Point(mid_x, mid_y)
    
    def distanceFromPoint(self, pt):
        A = pt.x - self.x1
        B = pt.y - self.y1
        C = self.x2 - self.x1
        D = self.y2 - self.y1
        
        dot = A*C + B*D
        len_sq = C*C + D*D
        param = -1
        if(len_sq != 0):
            param = dot / len_sq
            
        xx = 0.0
        yy = 0.0
        
        if param <0:
            xx = self.x1
            yy = self.y1
        elif param > 1:
            xx = self.x2
            yy = self.y2
        else:
            xx = self.x1 + param*C
            yy = self.y1 + param*D
            
        dx = pt.x - xx
        dy = pt.y - yy
        
        return math.sqrt(dx*dx + dy*dy)
    
    def pointOn(self, pt):
        btwnx1 = (self.x1 <= pt.x and pt.x <= self.x2)
        btwnx2 = (self.x2 <= pt.x and pt.x <= self.x1)
        if not btwnx1 and not btwnx2:
            return False
        
        btwny1 = (self.y1 <= pt.y and pt.y <= self.y2)
        btwny2 = (self.y2 <= pt.y and pt.y <= self.y1)
        return btwny1 or btwny2
    
    def orientation(self, pt):
        val = ((self.y2 - self.y1) * (pt.x - self.x2)) - ((self.x2 - self.x1) * (pt.y - self.y2))
        if val > 0:
            return Segment.CLOCKWISE
        elif val < 0:
            return Segment.COUNTERCLOCKWISE
        else:
            return Segment.COLINEAR
            
    
    def intersectsWithSegment(self, seg):
        p1 = Point(self.x1, self.y1)
        q1 = Point(self.x2, self.y2)
        
        p2 = Point(seg.x1, seg.y1)
        q2 = Point(seg.x2, seg.y2)
        
        o1 = self.orientation(p2)
        o2 = self.orientation(q2)
        o3 = seg.orientation(p1)
        o4 = seg.orientation(q1)
        
        if o1 != o2 and o3 != o4:
            return True
        
        if(o1 == 0 and self.pointOn(p2)) or (o2 == 0 and self.pointOn(q2)):
            return True
        if(o3 == 0 and seg.pointOn(p1)) or (o4 == 0 and seg.pointOn(q1)):
            return True
        
        return False
        
    def line(self):
        endpts = self.endpoints()
        return endpts[0].line_through_point(endpts[1])
                               
    def draw(self, turtle, boundingRect):  #turtle canvas is a bit more than 350 x 350 so we scale 100 x 100 to this size
        turtleSeg = self.scaleToTurtleCanvas(boundingRect)
        turtle.penup()
        turtle.goto(turtleSeg.x1, turtleSeg.y1)
        turtle.pendown()
        turtle.goto(turtleSeg.x2,turtleSeg.y2)
        turtle.penup()


class Rect:  #Really an axis-aligned rectangle

    """A rectangle identified by two points.

    The rectangle stores left, top, right, and bottom values.

    Coordinates are based on screen coordinates.

    origin                               top
       +-----> x increases                |
       |                           left  -+-  right
       v                                  |
    y increases                         bottom

    set_points  -- reset rectangle coordinates
    contains  -- is a point inside?
    overlaps  -- does a rectangle overlap?
    top_left  -- get top-left corner
    bottom_right  -- get bottom-right corner
    expanded_by  -- grow (or shrink)
    """

    def __init__(self, pt1, pt2):
        """Initialize a rectangle from two points."""
        self.set_points(pt1, pt2)

    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        (x1, y1) = pt1.as_tuple()
        (x2, y2) = pt2.as_tuple()
        self.left = min(x1, x2)
        self.top = min(y1, y2)
        self.right = max(x1, x2)
        self.bottom = max(y1, y2)
        
    def toJSON(self):  #we do this from the Turtle perspective, which is also conventional x,y coords
        turtle_top_left = Point(self.left, self.bottom)
        turtle_bottom_right = Point(self.right, self.top)
        return "{\"top_left\": " + turtle_top_left.toJSON() + ", \"bottom_right\": " + turtle_bottom_right.toJSON() + "}"

    def contains(self, pt):
        """Return true if a point is inside the rectangle."""
        x,y = pt.as_tuple()
        return (self.left <= x <= self.right and
                self.top <= y <= self.bottom)

    def overlaps(self, other):
        """Return true if a rectangle overlaps this rectangle."""
        return (self.right > other.left and self.left < other.right and
                self.top < other.bottom and self.bottom > other.top)
    
    def top_left(self):
        """Return the top-left corner as a Point."""
        return Point(self.left, self.top)
    
    def bottom_right(self):
        """Return the bottom-right corner as a Point."""
        return Point(self.right, self.bottom)
    
    def expanded_by(self, n):
        """Return a rectangle with extended borders.

        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "n" points.
        """
        p1 = Point(self.left-n, self.top-n)
        p2 = Point(self.right+n, self.bottom+n)
        return Rect(p1, p2)
    
    def __str__( self ):
        return "<Rect (%s,%s)-(%s,%s)>" % (self.left,self.top,
                                           self.right,self.bottom)
    
    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__,
                               Point(self.left, self.top),
                               Point(self.right, self.bottom))
                               
    def segments(self):  
        topLeft = Point(self.left, self.top)
        topRight = Point(self.right, self.top)
        bottomLeft = Point(self.left, self.bottom)
        bottomRight = Point(self.right, self.bottom)
        segs = []
        segs.append(Segment(topLeft, topRight)) 
        segs.append(Segment(topRight, bottomRight))
        segs.append(Segment(bottomLeft, bottomRight))
        segs.append(Segment(topLeft, bottomLeft))
        return segs
                               
    def distanceFromPoint(self, pt):
        segs = self.segments()
        return min(segs[0].distanceFromPoint(pt), segs[1].distanceFromPoint(pt),
            segs[2].distanceFromPoint(pt), segs[3].distanceFromPoint(pt))
            
    def center(self):
        return Point((self.left + self.right)/2.0, (self.top + self.bottom)/2.0)
                               
    def scaleToTurtleCanvas(self):
        turtle_left = (self.left / 100)*700 - 350
        turtle_right = (self.right / 100)*700 -350
        turtle_top = (self.top / 100)*700 - 350
        turtle_bottom = (self.bottom / 100)*700 -350
        
        tl = Point(turtle_left, turtle_top)
        br = Point(turtle_right, turtle_bottom)
        return Rect(tl, br)
                               
    def draw(self, turtle):  #turtle canvas is a bit more than 350 x 350 so we scale 100 x 100 to this size
        turtleRect = self.scaleToTurtleCanvas()
        turtle.penup()
        turtle.goto(turtleRect.left, turtleRect.top)
        turtle.pendown()
        turtle.goto(turtleRect.right,turtleRect.top)
        turtle.goto(turtleRect.right,turtleRect.bottom)
        turtle.goto(turtleRect.left,turtleRect.bottom)
        turtle.goto(turtleRect.left, turtleRect.top)
        turtle.penup()
  
class Triangle:
    def __init__(self, pt1, pt2, pt3):
        self.pt1 = pt1
        self.pt2 = pt2
        self.pt3 = pt3
        
    def pointInside(self, pt):  #tests whether point is in the interior, so NOT on the boundary!
        seg1 = Segment(self.pt1, self.pt2)
        seg2 = Segment(self.pt2, self.pt3)
        seg3 = Segment(self.pt3, self.pt1)
        o1 = seg1.orientation(pt)
        o2 = seg2.orientation(pt)
        o3 = seg3.orientation(pt)
        
        return o1 == o2 and o2 == o3
        
    def intersectsWithSegment(self, seg):
        seg1 = Segment(self.pt1, self.pt2)
        if seg.intersectsWithSegment(seg1):
            return True
        seg2 = Segment(self.pt2, self.pt3)
        if seg.intersectsWithSegment(seg2):
            return True
        seg3 = Segment(self.pt3, self.pt1)
        if seg.intersectsWithSegment(seg3):
            return True
        return self.pointInside(Point(seg.x1, seg.y1)) or self.pointInside(Point(seg.x2, seg.y2))
    