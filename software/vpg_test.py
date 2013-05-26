from SimpleCV import *
import serial
from vpg_constants import *
from vpg_funcs import *
from vpg_button import *
import time, sys
from math import hypot

myPort = serial.Serial('/dev/ttyUSB0', 38400, timeout = 10)

cam = Camera()

i = cam.getImage()
i = cam.getImage()

while TRUE:
  while '0' not in buttonCheck():
    i = cam.getImage().grayscale()
    i.show()

  i = cam.getImage()
  i = cam.getImage()
  i = cam.getImage().grayscale()
  
  startToOpDist = 38.5
  opToOpDist = 37

  ## Identify start tiles by finding a blob that is nicely large.
  blobList = i.findBlobs(threshval = -1, minsize = 2000, maxsize = 4000)

  if blobList is None:
    print "No start tile found!"
    continue
    
  elif blobList is not None:
    blobList.draw(width = -1, color = blue)
    startTileCenter = blobList[0].centroid()
    startTileYSize = blobList[0].minRectHeight()
    startTileXSize = blobList[0].minRectWidth()
    pixelSize = 20 / ((startTileYSize + startTileXSize)/2)
    
  print "Start tile center = " + str(startTileCenter)
  print "Pixel size = " + str(pixelSize)

  ## This next bit is just making it easier later on to do math based on the
  ##  center of the start tile. x0 and y0 become the origin for further
  ##  trigonometry to find things.
  x0 = startTileCenter[0]
  y0 = startTileCenter[1]

  ## Identify command tiles.
  commandTileBlobs = i.findBlobs(threshval = -1, minsize = 100, maxsize = 200, threshconstant = 25)
  circleBlobs = []
  commandBlobs = []

  if commandTileBlobs is None:
    print "No command blobs found!"
    continue

  ## We've found blobs that are the right size for command tiles. Now we need
  ##  to create a list of those blobs. Right now, we're going to leave them
  ##  unsorted.
  elif commandTileBlobs is not None:
    for blob in commandTileBlobs:
      blobRatio = blob.minRectWidth() / blob.minRectHeight()
      if blobRatio < 1.2 and blobRatio > .8:
        x1 = blob.centroid()[0]
        y1 = blob.centroid()[1]
        distToStartTile = hypot(x1-x0,y1-y0)
        circleBlobs.append([blob, distToStartTile, blob.centroid()])
      else:
        x1 = blob.centroid()[0]
        y1 = blob.centroid()[1]
        distToStartTile = hypot(x1-x0,y1-y0)
        commandBlobs.append([blob,distToStartTile, blob.centroid()])

  ## Catch any failures to find fids and commands here.
  if len(circleBlobs) == 0:
    print "No fids found!"
    continue
  if len(commandBlobs) == 0:
    print "No commands found!"
    continue
  
  ## Time to sort blobs! We want to start at the centroid of the start block,
  ##  then order our blobs from closest to farthest away from that block. This
  ##  gives us two things: an order of execution, and a way to determine which
  ##  command goes with which circle. The angle between the circle and the
  ##  command is what gives the command meaning.      

  circleBlobs = sorted(circleBlobs, key=lambda blob: blob[1])
  commandBlobs = sorted(commandBlobs, key=lambda blob: blob[1])

  ## Okay, now that we have our circles and commands figured out, we can start
  ##  figuring out what the commands are, exactly. To do this, we need to know
  ##  two things: the angle of the overall train of tiles, and the deviation
  ##  of a line drawn from a circle to its corresponding command blob relative
  ##  to that overall angle.

  ## Calculate the overall angle by finding the centroid of the last circle in
  ##  the train and drawing a line between that and the center of the start tile
  ##  (which, if you'll remember, we set to (x0,y0) up above)
  x1 = circleBlobs[-1][2][0]
  y1 = circleBlobs[-1][2][1]
  trainAngle = degrees(atan2(y1-y0, x1-x0))
  trainAngleLine = DrawingLayer((i.width, i.height))
  trainAngleLine.line(startTileCenter, circleBlobs[-1][2], color = white, width = 1)
  i.addDrawingLayer(trainAngleLine)
  print "Train angle = " + str(trainAngle)

  for blob in circleBlobs:
    blob[0].draw(width = -1, color = yellow)

  for blob in commandBlobs:
    blob[0].draw(width = -1, color = red)
    
  if len(commandBlobs) != len(circleBlobs):
    print "Did not find same number of fids and commands!"
    print "Found " + str(len(circleBlobs)) + " fids for " + str(len(commandBlobs)) + " commands"
    i.show()
    time.sleep(2)
    continue

  ## Create a list of commands. Each command will be based on the angle from
  ##  the center of a circle to the center of its corresponding command blob,
  ##  minus the train angle.
  commandList = []
  commandAngleLines = DrawingLayer((i.width,i.height))
  for j in range(0, len(circleBlobs)):
    x1 = circleBlobs[j][2][0]
    y1 = circleBlobs[j][2][1]
    x2 = commandBlobs[j][2][0]
    y2 = commandBlobs[j][2][1]
    cmdDist = hypot(x2-x1, y2-y1)
    commandAngleLines.line(circleBlobs[j][2],commandBlobs[j][2], color = white, width = 1)
    localAngle = degrees(atan2(y2-y1,x2-x1))
    commandList.append(localAngle-trainAngle)

  i.addDrawingLayer(commandAngleLines)
  i.applyLayers()

  print "Command angles:"
  commandText = []
  for item in commandList:
    commandText.append(str(extractCommand(item))[0])
    
  i.show() 
  for command in commandText:
    myPort.write(command)
    
  print "All done!"