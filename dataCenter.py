import turtle
import time
import random
from mip import *
import math
import logging

from geometry2D import *

class Rack:
    UP = -1
    DOWN = -2
    RIGHT = -3
    LEFT = -4
    BOTH_SIDES = -9
    
    ticky_length = 0.5 #perhaps make this a function of DataCenter.epsilon
    
    def __init__(self, seg, direction = LEFT):
        self.seg = seg
        self.dir = direction
        
    def setDir(self, direction):
        self.dir = direction
        
    def draw(self, tt, boundingRect, withTickies=True):
        #at this point just draws vertical racks
        self.seg.draw(tt, boundingRect)
        if withTickies:
            offsetPt = Point()
            midpt = self.seg.midpoint()
            if self.dir == Rack.DOWN: 
                offsetPt = Point(midpt.x, midpt.y - Rack.ticky_length)
            elif self.dir == Rack.RIGHT:
                offsetPt = Point(midpt.x + Rack.ticky_length, midpt.y)
            elif self.dir == Rack.UP:
                offsetPt = Point(midpt.x, midpt.y + Rack.ticky_length)
            else: #self.dir == LEFT   
                offsetPt = Point(midpt.x - Rack.ticky_length, midpt.y)                    
            tickySeg = Segment(midpt, offsetPt)    
            originalWidth = tt.width()
            tt.width(4)
            tickySeg.draw(tt, boundingRect)
            tt.width(originalWidth)  #default width
            
    def guardingDirToString(self):
        if(self.dir == Rack.UP): 
            return "FROM ABOVE"
        elif(self.dir == Rack.RIGHT):
            return "FROM RIGHT"
        elif(self.dir == Rack.DOWN):
            return "FROM BELOW"
        elif(self.dir == Rack.LEFT):
            return "FROM LEFT"
        else:
            return "FROM BOTH SIDES"
            
    def toString(self):
        return "endpts: (" + str(self.seg.x1) + "," + str(self.seg.y1) + "), ("  + str(self.seg.x2) + "," + str(self.seg.y2) + "), guarding_dir = " + self.guardingDirToString()

class GrowableRack(Rack):
    def __init__(self, seg, direction = Rack.LEFT):
        super().__init__(seg, direction)
        self.setGrowthPossibilities()
        
    def setDir(self, direction):
        super().setDir(self, direction)
        self.setGrowthPossibilities()
        
    def setGrowthPossibilities(self):
        if self.dir == Rack.LEFT or self.dir == Rack.RIGHT:
            self.can_grow_up = True
            self.can_grow_down = True
            self.can_grow_right = False
            self.can_grow_left = False
        if self.dir == Rack.UP or self.dir == Rack.DOWN:
            self.can_grow_up = False
            self.can_grow_down = False
            self.can_grow_right = True
            self.can_grow_left = True
            
class Guard:  #also known as a camera
    GUARD_CANDIDATE_COLOR = "green"
    GUARD_SELECTED_COLOR = "red"
    GUARD_DRAWING_RADIUS = 5 #in pixels
    
    def __init__(self, where):
        self.loc = where
        self.selected = False
        
    def draw(self, turtle, boundingRect, drawCandidateGuards=False):
        if not self.selected:
            if not drawCandidateGuards:
                return
            else:
                drawingColor = Guard.GUARD_CANDIDATE_COLOR
        else:
            drawingColor = Guard.GUARD_SELECTED_COLOR
            
        self.loc.draw_circle_centered_at(turtle, Guard.GUARD_DRAWING_RADIUS, boundingRect, 
                                         filled=True, color=drawingColor)
        
    def toString(self):
        return "loc: (" + str(self.loc.x) + "," + str(self.loc.x) + ")"
            
            
class DataCenterGrid:
    GRID_COLOR = "grey"
    
    def __init__(self, bdingRect, racks = []):
        self.vertices = set()
        for rack in racks:
            for endpt in rack.seg.endpoints():
                self.vertices.add(endpt)
            self.x_crosspts = set()
            self.y_crosspts = set()
        
        for vertex in self.vertices:
            self.x_crosspts.add(vertex.x)
            self.y_crosspts.add(vertex.y)
        self.boundingRect = bdingRect
        self.rackSet = racks
        self.cells = []
        self.candidateGuardSet = []
        
    def refineGrid(self): # Refine by splitting every cell into 4 congruent rectangular pieces
        # Place an additional vertex at the center of the original set of cells, 
        # add to x_crosspots and y_crosspts and we're done!
        for cell in self.cells:
            midpt = cell.center()
            self.vertices.add(midpt)
            self.x_crosspts.add(midpt.x)
            self.y_crosspts.add(midpt.y)
        
    def getCells(self):
        x_crosses = [self.boundingRect.left]
        for x_cross in self.x_crosspts:
            x_crosses.append(x_cross) 
        x_crosses.append(self.boundingRect.right)
        x_crosses.sort()
        y_crosses = [self.boundingRect.top]
        for y_cross in self.y_crosspts:
            y_crosses.append(y_cross) 
        y_crosses.append(self.boundingRect.bottom)
        y_crosses.sort()
        
        self.cells.clear()
        for i in range(len(x_crosses) - 1):
            for j in range(len(y_crosses) - 1):
                topLeft = Point(x_crosses[i], y_crosses[j])
                bottomRight = Point(x_crosses[i+1], y_crosses[j+1])
                self.cells.append(Rect(topLeft, bottomRight))
        
        return self.cells
        
    def generateCandidateGuardSet(self):
        self.getCells()
        self.candidateGuardSet.clear()
        for cell in self.cells:
            self.candidateGuardSet.append(Guard(cell.center()))
        return self.candidateGuardSet
        
            
    def draw(self, turtle, boundingRect):
        turtle.color(DataCenterGrid.GRID_COLOR)
        
        for x in self.x_crosspts:
            topPt = Point(x, boundingRect.top)
            bottomPt = Point(x, boundingRect.bottom)
            gridLine = Segment(topPt, bottomPt)
            gridLine.draw(turtle, boundingRect)
            
        for y in self.y_crosspts:   
            leftPt = Point(boundingRect.left, y)
            rightPt = Point(boundingRect.right, y)
            gridLine = Segment(leftPt, rightPt)
            gridLine.draw(turtle, boundingRect) 
        
        turtle.color("black") #default color
        
    def drawGuardSet(self, turtle, boundingRect, drawCandidateGuards):
        for guard in self.candidateGuardSet:
            guard.draw(turtle, boundingRect, drawCandidateGuards)
            
        

class DataCenter:
    ORIENTATION_VERTICAL = -1
    ORIENTATION_HORIZONTAL = -2
    ORIENTATION_ORTHOGONAL = -3
    ORIENTATION_GENERIC = -4
    
    POSERS_CHOICE = -1
    SOLVERS_CHOICE = -2
    
    COMPLETE_COVERAGE = -1
    ALL_BUT_DELTA_COVERAGE = -2
    
    def __init__(self, rect, eps=2):
        self.boundaryRect = rect
        self.epsilon = eps
        self.racks = []
        self.grid = DataCenterGrid(self.boundaryRect)
        self.guardingModel = DataCenter.POSERS_CHOICE #default
        self.coverage = DataCenter.COMPLETE_COVERAGE
        self.delta = 0.0
        
    def setGuardingModel(self, model, coverageType, delta):
        self.guardingModel = model
        self.coverage = coverageType
        self.delta = delta
    
    def placeRacks(self, racks):
        self.racks = racks
        
    def placeRandomHStyleOrthogonalRacks(self, num):
        random.seed()
        self.racks = []
        
        orientations = []
        count_horizontal = 0
        for i in range(num):
            if i == 0 or orientations[i-1] == DataCenter.ORIENTATION_VERTICAL:
                if random.uniform(0.0, 1.0) <= 0.5:
                    orientations.append(DataCenter.ORIENTATION_VERTICAL)
                else:
                    orientations.append(DataCenter.ORIENTATION_HORIZONTAL)
                    count_horizontal += 1
            else:
                orientations.append(DataCenter.ORIENTATION_VERTICAL)
                
        if count_horizontal > 0:
            separation = ((100.0 - self.epsilon) - (num*self.epsilon))/count_horizontal
        else: 
            separation = ((100.0 - self.epsilon) - (num*self.epsilon))/num
            
        logging.info("Width of horizontal segments = " + str(separation))
        
        last_x = 0
        for i in range(num):
            dir = self.generateRandomDirection(orientations[i])
            if orientations[i] == DataCenter.ORIENTATION_VERTICAL:
                if count_horizontal > 0:
                    self.racks.append(Rack(Segment(Point(last_x + self.epsilon, self.epsilon), Point(last_x + self.epsilon, 100.0 - self.epsilon)), dir))
                    last_x = last_x + self.epsilon
                else:
                    self.racks.append(Rack(Segment(Point(last_x + self.epsilon + separation, self.epsilon), Point(last_x + self.epsilon + separation, 100.0 - self.epsilon)), dir))
                    last_x = last_x + self.epsilon + separation
            else:
                self.racks.append(Rack(Segment(Point(last_x + self.epsilon, 50.0), Point(last_x + self.epsilon + separation, 50.0)), dir))
                last_x = last_x + self.epsilon + separation
                
    def placeRandomOrthogonalRacks(self, num): #returns True of successful, False otherwise
        buffer = 0.1
        if (1.0 + buffer) * num*4*self.epsilon*self.epsilon > 100*100:
            logger.warning("Not enough room to place racks!")
            return false
        
        for i in range(num):
            keepLooping = True
            while keepLooping:
                x = 100.0 * random.uniform(0.0, 1.0)
                y = 100.0 * random.uniform(0.0, 1.0)
                pt = Point(x, y)
                if self.isPointSufficientlyFarFromOtherRacksAndBoundary(pt, 2*self.epsilon):  #give some room to grow
                    keepLooping = False
                    dirRandom = random.uniform(0.0, 1.0)
                    if dirRandom < 0.25:
                        dir = Rack.RIGHT
                    elif dirRandom < 0.50:
                        dir = Rack.DOWN
                    elif dirRandom < 0.75:
                        dir = Rack.LEFT
                    else:
                        dir = Rack.UP
                        
                    if dir == Rack.UP or dir == Rack.DOWN:
                        rack = GrowableRack(Segment(Point(x - self.epsilon/2.0, y), Point(x + self.epsilon/2.0, y)), dir)
                        self.racks.append(rack)
                    else:
                        rack = GrowableRack(Segment(Point(x, y - self.epsilon/2.0), Point(x, y + self.epsilon/2.0)), dir)
                        self.racks.append(rack)
                    
        someRacksGrew = true
        while someRacksGrew:
            someRacksGrew = self.growRacks()
            
    def growRacks(self):
        someRacksGrew = False
        for rack in self.racks:
            if rack.can_grow_right:
                growPt = Point(rack.seg.x2+1, rack.seg.y2)
                roomToGrow = self.isPointSufficientlyFarFromOtherRacksAndBoundary(growPt, thisRack=rack)
                if roomToGrow:
                    rack.seg.x2 += 1
                    someRacksGrew = True
            if rack.can_grow_left:
                growPt = Point(rack.seg.x1-1, rack.seg.y1)
                roomToGrow = self.isPointSufficientlyFarFromOtherRacksAndBoundary(growPt, thisRack=rack)
                if roomToGrow:
                    rack.seg.x1 -= 1
                    someRacksGrew = True
            if rack.can_grow_up:
                growPt = Point(rack.seg.x2, rack.seg.y2+1)
                roomToGrow = self.isPointSufficientlyFarFromOtherRacksAndBoundary(growPt, thisRack=rack)
                if roomToGrow:
                    rack.seg.y2 += 1
                    someRacksGrew = True
            if rack.can_grow_down:
                growPt = Point(rack.seg.x1, rack.seg.y1-1)
                roomToGrow = self.isPointSufficientlyFarFromOtherRacksAndBoundary(growPt, thisRack=rack)
                if roomToGrow:
                    rack.seg.y1 -= 1
                    someRacksGrew = True
        
        return someRacksGrew        
        
    def placeRandomAllVerticalRacks(self, num): 
        random.seed()
        racks = []
        xs = set()
        for i in range(num):
            keepLooping = True
            while keepLooping:
                x = 100.0 * random.uniform(0.0, 1.0)
                pt = Point(x, 50.0)
                if self.isPointSufficientlyFarFromOtherRacksAndBoundary(pt):
                    keepLooping = False
                    xs.add(x)
                    dir = self.generateRandomDirection(DataCenter.ORIENTATION_VERTICAL)
                    rack = Rack(Segment(Point(x, self.epsilon), Point(x, 100.0 - self.epsilon)), dir)
                    self.racks.append(rack)
                    print("x = " + str(x))
                    
        return racks
    
    def placeHStyleRackConfiguration(self, num):  #Note that this is a Poser's Choice placement
        self.racks = []
        
        orientations = []
        count_horizontal = 0
        for i in range(num):
            if i == 0 or i == 1 or i == num-1:
                orientations.append(DataCenter.ORIENTATION_VERTICAL)
            elif orientations[i-1] == DataCenter.ORIENTATION_VERTICAL and orientations[i-2] == DataCenter.ORIENTATION_VERTICAL:
                    orientations.append(DataCenter.ORIENTATION_HORIZONTAL)
                    count_horizontal += 1
            else:
                orientations.append(DataCenter.ORIENTATION_VERTICAL)
                
        if count_horizontal > 0:
            separation = ((100.0 - self.epsilon) - (num*self.epsilon))/count_horizontal
        else: 
            separation = ((100.0 - self.epsilon) - (num*self.epsilon))/num
        
        last_x = 0
        lastVerticalDir = Rack.LEFT
        for i in range(num):
            facingDir = Rack.UP #direction for all horizontal racks
            if orientations[i] == DataCenter.ORIENTATION_VERTICAL:
                if count_horizontal > 0:
                    if i == 0:
                        facingDir = Rack.LEFT
                    elif i == 1 or i == num-1:
                        facingDir = Rack.RIGHT
                    else:
                        if lastVerticalDir == Rack.LEFT:
                            facingDir = Rack.RIGHT
                        else:
                            facingDir = Rack.LEFT
                    lastVerticalDir = facingDir
                    self.racks.append(Rack(Segment(Point(last_x + self.epsilon, self.epsilon), Point(last_x + self.epsilon, 100.0 - self.epsilon)), facingDir))
                    last_x = last_x + self.epsilon
                else:
                    self.racks.append(Rack(Segment(Point(last_x + self.epsilon + separation, self.epsilon), Point(last_x + self.epsilon + separation, 100.0 - self.epsilon)), facingDir))
                    last_x = last_x + self.epsilon + separation
            else:
                self.racks.append(Rack(Segment(Point(last_x + self.epsilon, 50.0), Point(last_x + self.epsilon + separation, 50.0)), facingDir))
                last_x = last_x + self.epsilon + separation
        
    
    def isPointSufficientlyFarFromOtherRacksAndBoundary(self, pt, tolerance=0, thisRack=None):
        if tolerance == 0:
            tolerance = self.epsilon
            
        distanceToBoundary = self.boundaryRect.distanceFromPoint(pt)
        if(distanceToBoundary < tolerance):
            return false

        for rack in self.racks:
            if rack != thisRack:
                distanceFromRack = rack.seg.distanceFromPoint(pt)
                if distanceFromRack < tolerance:
                    return false
        #Does not yet handle distance to other segments
        return true
    

    def generateRandomDirection(self, orientation):
        r = random.uniform(0.0, 1.0)
        if(orientation == DataCenter.ORIENTATION_VERTICAL):
            if(r <= 0.5): 
                return Rack.RIGHT
            else:
                return Rack.LEFT
        elif(orientation == DataCenter.ORIENTATION_HORIZONTAL):
            if(r <= 0.5): 
                return Rack.UP
            else:
                return Rack.DOWN
        else:
            if(r <= 0.25):
                return Rack.UP
            elif(r <= 0.50):
                return Rack.RIGHT
            elif(r <= 0.75):
                return Rack.DOWN
            else:
                return Rack.LEFT
            
    def createInitialGrid(self):
        self.grid = DataCenterGrid(self.boundaryRect, self.racks)
        
    def guardCanSeeRack(self, guard_index, rack_index):  #currently just deals with orthog visibility
        # covers case of full coverage only
        if self.coverage == DataCenter.ALL_BUT_DELTA_COVERAGE:
            return self.guardCanSeeRackExceptForDelta(guard_index, rack_index)
        
        guard = self.grid.candidateGuardSet[guard_index]
        rack = self.racks[rack_index]
        # first check that guard is on right side of rack
        logging.debug("Guard " + guard.toString())
        logging.debug("Rack " + rack.toString())
        
        if self.guardingModel == DataCenter.POSERS_CHOICE:
            if rack.dir == Rack.RIGHT and guard.loc.x <= rack.seg.x1:
                logging.debug("CANNOT GUARD: WRONG SIDE!")
                return False
            elif rack.dir == Rack.LEFT and guard.loc.x >= rack.seg.x1:
                logging.debug("CANNOT GUARD: WRONG SIDE!")
                return False
            elif rack.dir == Rack.DOWN and guard.loc.y >= rack.seg.y1:
                logging.debug("CANNOT GUARD: WRONG SIDE!")
                return False
            elif rack.dir == Rack.UP and guard.loc.y <= rack.seg.y1:
                logging.debug("CANNOT GUARD: WRONG SIDE!")
                return False
        
        guardingTriangle = Triangle(guard.loc, Point(rack.seg.x1, rack.seg.y1),
                                             Point(rack.seg.x2, rack.seg.y2))
        for i in range(len(self.racks)):
            if i != rack_index:
                if(guardingTriangle.intersectsWithSegment(self.racks[i].seg)):
                    logging.debug("CANNOT GUARD! The following rack is blocking: " + rack.toString())
                    return False
        logging.debug("SUCCESSFUL GUARD!")
        return True         
    
    def guardCanSeeRackExceptForDelta(self, guard_index, rack_index): 
        # covers case of full coverage only
        guard = self.grid.candidateGuardSet[guard_index]
        rack = self.racks[rack_index]
        # first check that guard is on right side of rack
        logging.debug("Guard " + guard.toString())
        logging.debug("Rack " + rack.toString())
        
        if self.guardingModel == DataCenter.POSERS_CHOICE:
            if rack.dir == Rack.RIGHT and guard.loc.x <= rack.seg.x1:
                logging.debug("CANNOT GUARD: WRONG SIDE!")
                return False
            elif rack.dir == Rack.LEFT and guard.loc.x >= rack.seg.x1:
                logging.debug("CANNOT GUARD: WRONG SIDE!")
                return False
            elif rack.dir == Rack.DOWN and guard.loc.y >= rack.seg.y1:
                logging.debug("CANNOT GUARD: WRONG SIDE!")
                return False
            elif rack.dir == Rack.UP and guard.loc.y <= rack.seg.y1:
                logging.debug("CANNOT GUARD: WRONG SIDE!")
                return False
        
        guardingTriangle = Triangle(guard.loc, Point(rack.seg.x1, rack.seg.y1),
                                             Point(rack.seg.x2, rack.seg.y2))
        for i in range(len(self.racks)):
            if i != rack_index:
                pt1Inside = guardingTriangle.pointInside(Point(self.racks[i].seg.x1, self.racks[i].seg.y1))
                pt2Inside = guardingTriangle.pointInside(Point(self.racks[i].seg.x2, self.racks[i].seg.y2))
                if not pt1Inside and  not pt2Inside: #case where we see the entire segment or nothing at all
                    if guardingTriangle.intersectsWithSegment(self.racks[i].seg):
                        return rack.seg.length() <= self.delta
                elif pt1Inside and pt2Inside:
                    rackLine = rack.seg.line()
                    pointingLine1 = guard.loc.line_through_point(Point(self.racks[i].seg.x1, self.racks[i].seg.y1))
                    pointingLine2 = guard.loc.line_through_point(Point(self.racks[i].seg.x2, self.racks[i].seg.y2))
                    ptOnRack1 = rackLine.intersectionWithLine(pointingLine1)
                    ptOnRack2 = rackLine.intersectionWithLine(pointingLine2)
                    if ptOnRack1.distance_to(ptOnRack2) > self.delta:
                        return False
                elif pt1Inside: #just pt1Inside
                    rackLine = rack.seg.line()
                    pointingLine = guard.loc.line_through_point(Point(self.racks[i].seg.x1, self.racks[i].seg.y1))
                    rackTop = Point(rack.seg.x1, rack.seg.y1)
                    topGuardingTriangleSeg = Segment(guard.loc, rackTop)
                    ptOnRack = rackLine.intersectionWithLine(pointingLine)
                    if topGuardingTriangleSeg.intersectsWithSegment(self.racks[i].seg) and rackTop.distance_to(ptOnRack) > self.delta:
                        return False
                    else:
                        rackBottom = Point(rack.seg.x2, rack.seg.y2)
                        if rackBottom.distance_to(ptOnRack) > self.delta:
                            return False
                else: #just pt2Inside
                    rackLine = rack.seg.line()
                    pointingLine = guard.loc.line_through_point(Point(self.racks[i].seg.x2, self.racks[i].seg.y2))
                    rackTop = Point(rack.seg.x1, rack.seg.y1)
                    topGuardingTriangleSeg = Segment(guard.loc, rackTop)
                    ptOnRack = rackLine.intersectionWithLine(pointingLine)
                    if topGuardingTriangleSeg.intersectsWithSegment(self.racks[i].seg) and rackTop.distance_to(ptOnRack) > self.delta:
                        return False
                    else:
                        rackBottom = Point(rack.seg.x2, rack.seg.y2)
                        if rackBottom.distance_to(ptOnRack) > self.delta:
                            return False
                    
        logging.debug("SUCCESSFUL GUARD!")
        return True         
        
    def generateGuardingMatrix(self):
        #ijth entry tells whether the jth guard can see ith rack
        self.grid.guardingMatrix = []
        for i in range(len(self.racks)):
            rackGuardSet = []
            for j in range(len(self.grid.candidateGuardSet)):
                if self.guardCanSeeRack(j, i):
                    rackGuardSet.append(1)
                else:
                    rackGuardSet.append(0)
            self.grid.guardingMatrix.append(rackGuardSet)        
                
    def findMinimalGuardSet(self):
        model = Model(sense=MINIMIZE)

        G = [model.add_var(var_type=BINARY) for i in range(len(self.grid.candidateGuardSet))]
            
        for i in range(len(self.racks)): 
            model += xsum(self.grid.guardingMatrix[i][j]*G[j] for j in range(len(self.grid.candidateGuardSet))) >= 1
        
        model.objective = minimize(xsum(G[i]  for i in range(len(self.grid.candidateGuardSet))))
        
        #self.grid.selectedGuards = []
        model.max_mip_gap = 0.05
        status = model.optimize(max_seconds=60)
        if status == OptimizationStatus.OPTIMAL:
            logging.info("Optimal solution cost: " + str(int(model.objective_value)) + " found from " + str(len(self.grid.candidateGuardSet)) + " candidates")
            iter = 0
            numGuards = 0
            for v in model.vars:
                logging.debug('{} : {}'.format(v.name, v.x))
                if v.x == 1:
                    self.grid.candidateGuardSet[iter].selected = True  
                    numGuards += 1                  
                    #self.grid.selectedGuards.append(iter)
                iter += 1
            return numGuards  
        
    def draw(self, tt, drawGrid=False, drawCandidateGuards=False):
        tt.width(3) 
        self.boundaryRect.draw(tt)
        
        tt.width(2)
        for i in range(len(self.racks)):
            self.racks[i].draw(tt, self.boundaryRect, withTickies=(self.guardingModel == DataCenter.POSERS_CHOICE))
            
        tt.width(1)
        if drawGrid:
            self.grid.draw(tt, self.boundaryRect)
            
        
        self.grid.drawGuardSet(tt, self.boundaryRect, drawCandidateGuards)
            
        tt.hideturtle()