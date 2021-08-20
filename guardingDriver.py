import turtle
import logging
import os
import shutil

from geometry2D import *
from dataCenter import *

EPSILON = 3.0
NUM_RACKS = 20
SLEEP_TIME_AT_END_OF_DRAWING = 5
HARD_NUM_ITERATIONS = 6
TURTLE_SPEED = 0
SAVE_TO_FILE = True
LOAD_DC_FROM_STORED_JSON = True

SAVED_IMAGES = "images/"
BACKED_UP_IMAGES = SAVED_IMAGES + "backup/" #saves images from prior run (only)

LOG_LEVEL = logging.INFO #prints logging.info() statements but not logging.debug() statements

logging.getLogger().setLevel(LOG_LEVEL)

def deleteAllFilesInDir(directory):
    for f in os.listdir(directory):
        if f.endswith(".eps") or f.endswith(".json"): #don't mess with subdirs
            os.remove(os.path.join(directory, f))
        
def copyAllFiles(sourceDir, destinationDir):
    for f in os.listdir(sourceDir):
        if f.endswith(".eps") or f.endswith(".json"): #don't mess with subdirs
            shutil.copy2(sourceDir + f, destinationDir + f)

#if we will save copies of the canvas take care of necessary preliminaries
if SAVE_TO_FILE:
    deleteAllFilesInDir(BACKED_UP_IMAGES)
    copyAllFiles(SAVED_IMAGES, BACKED_UP_IMAGES)
    deleteAllFilesInDir(SAVED_IMAGES)
    

# Data Center logical coordinates
topLeft = Point(0.0, 0.0)  
bottomRight = Point(100.0, 100.0)
boundingRect = Rect(topLeft, bottomRight)

dataCenter = None
res = False #turns True if able to successfully place requested racks

if LOAD_DC_FROM_STORED_JSON:
    dataCenter = DataCenter.FromJSONFile("saved_json/data_center0.json")
    if dataCenter != None:
        res = True
else:
    dataCenter = DataCenter(boundingRect, EPSILON)
    #dataCenter.setGuardingModel(dataCenter.POSERS_CHOICE)
    dataCenter.setGuardingModel(DataCenter.POSERS_CHOICE, DataCenter.COMPLETE_COVERAGE, delta=10)
    #res = dataCenter.placeRandomAllVerticalRacks(NUM_RACKS)   #generate 10 random vertical racks
    #res = dataCenter.placeRandomHStyleOrthogonalRacks(NUM_RACKS)
    #res = dataCenter.placeHStyleRackConfiguration(NUM_RACKS)
    res = dataCenter.placeRandomOrthogonalRacks(NUM_RACKS, growthMethod=DataCenter.GROW_ONE_BY_ONE)

if not res:
    logging.error("Could not create requisite number of racks! Aborting.")
    sys.exit() 

dataCenter.createInitialGrid()

tt = turtle.Turtle();
tt.speed(TURTLE_SPEED)
iters = 0
while iters < HARD_NUM_ITERATIONS:
    dataCenter.grid.generateCandidateGuardSet()
    dataCenter.generateGuardingMatrix()
    numGuards = dataCenter.findMinimalGuardSet()
    tt.clear()
    dataCenter.draw(tt, drawGrid=True, drawCandidateGuards=False)
    tt.setpos(-140, -380)
    tt.pendown()
    tt.write("# Segments = " + str(NUM_RACKS) + ", # Guards = " + str(numGuards), font=("Arial", 20, "normal"))
    tt.penup()
    time.sleep(SLEEP_TIME_AT_END_OF_DRAWING)
    if SAVE_TO_FILE:
        turtleScreen = tt.getscreen()
        turtleScreen.getcanvas().postscript(file=SAVED_IMAGES + "data_center" + str(iters) + ".eps")
        jsonFile = open(SAVED_IMAGES + "data_center" + str(iters) + ".json", "w")
        jsonFile.write(dataCenter.toJSON())
        jsonFile.close()
    iters += 1
    dataCenter.grid.refineGrid()

print("Done!")