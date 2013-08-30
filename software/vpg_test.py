from SimpleCV import *
import serial
from vpg_constants import *
from vpg_funcs import *
from vpg_button import *
import time, sys
from math import hypot

displayResolution = (640,480)

## This is a USB serial port, which is attached to an XBee module. This
##  is how the commands get relayed to the robot.
myPort = serial.Serial('/dev/ttyUSB0', 9600, timeout = 10)
setSerPins()
lcdPort = serial.Serial('/dev/ttyS1', 115200, timeout = 10)

## Create a SimpleCV camera object. This is how we get images.
cam = Camera()

## Create a SimpleCV image object by getting an image from the camera. We
##  do this twice here because some webcams won't capture a pretty image on
##  the first go, probably due to shuttering issues.
cam.getImage()
i = cam.getImage()

def processImage():
  lcdPort.write("|")
  lcdPort.write(chr(0))
  lcdPort.write("Processing begun!\n\r")
  ## Okay, we've had a request for a process. We want to clear the display
  ##  window, because there's some kind of memory leak in the display which
  ##  can cause crashes if the display window is allowed to be open too long.

  displayWindow = Display(resolution = displayResolution)
  i = cam.getImage().grayscale()
  i.save(displayWindow)
  
  ## Not using these yet, but they are the distances (in mm) between the center
  ##  of the start tile and the first fiducial and then from the center of one
  ##  fid to the next. We *could* use these, plus the train angle calculated
  ##  from the shape of the start tile, to determine search zones for commands,
  ##  increasing robustness against other junk on the table and, probably,
  ##  the speed with which the blobs are found. Not yet, though.
  startToOpDist = 38.5
  opToOpDist = 37

  ## Identify the start tile by finding a blob that is nicely large.
  blobList = i.findBlobs(threshval = -1, minsize = 1500, maxsize = 6000)

  ## Catch any errors and return to start if there are any.
  if blobList is None:
    print "No start tile found!"
    lcdPort.write("|")
    lcdPort.write(chr(0))
    lcdPort.write("No start tile found!")
    time.sleep(5.0)
    return
  
  ## If there *weren't* any errors, we'll want to do some stuff with the results.
  elif blobList is not None:
    lcdPort.write("Start tile found!\n\r")
    print "Start tile found!"
    ## Draw the start tile in blue on the image.
    blobList.draw(width = -1, color = blue)
    ## Create a tuple which has x,y of the center of the start tile.
    startTileCenter = blobList[0].centroid()
    ## Calculate the width and height of the square.
    startTileYSize = blobList[0].minRectHeight()
    startTileXSize = blobList[0].minRectWidth()
    ## Average the width and height (ideally, they should be the same) and calculate
    ##  the size of a pixel in the FOV, based on the fact that the start tile artifact
    ##  is 20mm to a side.
    pixelSize = 20 / ((startTileYSize + startTileXSize)/2)
  
  ## Print out the information we just calculated.
  ##print "Start tile center = " + str(startTileCenter)
  ##print "Pixel size = " + str(pixelSize)

  ## This next bit is just making it easier later on to do math based on the
  ##  center of the start tile. x0 and y0 become the origin for further
  ##  trigonometry to find things.
  x0 = startTileCenter[0]
  y0 = startTileCenter[1]

  ## Identify command tiles. A command tile is a circular fiducial with 1/4 of a ring 
  ##  concentric to it. The area of the fiducial and the ring segment are fairly similiar,
  ##  and both are much smaller than the start tile, so we can window down our search to
  ##  only blobs that are within a certain range.
  blobList = i.findBlobs(threshval = -1, minsize = 80, maxsize = 350)##, threshconstant = 25)

  ## Create a couple of empty arrays to store the fiducials and commands. We'll want to separate
  ##  them, then make sure we have the same number of each, then parse the commands.
  fidBlobs = []
  commandBlobs = []

  if blobList is None:
    lcdPort.write("|")
    lcdPort.write(chr(0))
    lcdPort.write("No command tiles!")
    print "No command tiles!"
    time.sleep(5.0)
    return
  ## We've found blobs that are the right size for command tiles. Now we need
  ##  to create a list of those blobs. Right now, we're going to leave them
  ##  unsorted.
  elif blobList is not None:
    for blob in blobList:
      blob.draw(width = -1, color = green)
      print blob.area()
    i.save(displayWindow)
    print "Commands found!"
    lcdPort.write("Commands found!\r\n")
    time.sleep(2)
    
    ## Iterate over the potential commands and fiducials, sorting them into
    ##  bins based on whether they're commands or fids.
    for blob in blobList:
      blobRatio = blob.minRectWidth() / blob.minRectHeight()
      ## if the ratio of the blob is close to 1, it's *probably* a fid, since
      ##  those are all circular.
      if blobRatio < 1.2 and blobRatio > .8:
        ## For both fids and commands, we're going to append a matrix of three
        ##  items to the list: the blob object itself, the distance to the start
        ##  tile, and the centroid. We'll calculate the distance to the start
        ##  tile by using hypot().
        x1 = blob.centroid()[0]
        y1 = blob.centroid()[1]
        distToStartTile = hypot(x1-x0,y1-y0)
        fidBlobs.append([blob, distToStartTile, blob.centroid()])
      else:
        x1 = blob.centroid()[0]
        y1 = blob.centroid()[1]
        distToStartTile = hypot(x1-x0,y1-y0)
        commandBlobs.append([blob,distToStartTile, blob.centroid()])

  blobList = []
  
  ## Catch any failures to find fids and commands here.
  if len(fidBlobs) == 0:
    lcdPort.write("|")
    lcdPort.write(chr(0))
    lcdPort.write("No fiducials!")
    print "No fiducials!"
    time.sleep(5.0)
    return
  else:
    fidString = str(len(fidBlobs)) + " fids found.\n\r"
    print fidString
    lcdPort.write(fidString)
    time.sleep(.5)
  if len(commandBlobs) == 0:
    lcdPort.write("|")
    lcdPort.write(chr(0))
    lcdPort.write("No commands!")
    print "No commands!"
    time.sleep(5.0)
    return
  else:
    comString = str(len(commandBlobs)) + " commands found.\n\r"
    print comString
    lcdPort.write(comString)
    time.sleep(.5)
  
  ## Time to sort blobs! We want to start at the centroid of the start block,
  ##  then order our blobs from closest to farthest away from that block. This
  ##  gives us two things: an order of execution, and a way to determine which
  ##  command goes with which circle. The angle between the circle and the
  ##  command is what gives the command meaning. We're going to sort the lists
  ##  in place.

  fidBlobs = sorted(fidBlobs, key=lambda blob: blob[1])
  commandBlobs = sorted(commandBlobs, key=lambda blob: blob[1])
  
  ## Okay, now that we have our circles and commands figured out, we can start
  ##  figuring out what the commands are, exactly. To do this, we need to know
  ##  two things: the angle of the overall train of tiles, and the deviation
  ##  of a line drawn from a circle to its corresponding command blob relative
  ##  to that overall angle.

  ## Calculate the overall angle by finding the centroid of the last circle in
  ##  the train and drawing a line between that and the center of the start tile
  ##  (which, if you'll remember, we set to (x0,y0) up above).
  x1 = fidBlobs[-1][2][0]
  y1 = fidBlobs[-1][2][1]
  trainAngle = degrees(atan2(y1-y0, x1-x0))
  trainAngleLine = DrawingLayer((i.width, i.height))
  trainAngleLine.line(startTileCenter, fidBlobs[-1][2], color = white, width = 1)
  i.addDrawingLayer(trainAngleLine)

  ## Take a break from hard stuff to draw in the fids and commands.
  for blob in fidBlobs:
    blob[0].draw(width = -1, color = yellow)

  for blob in commandBlobs:
    blob[0].draw(width = -1, color = red)
  
  ## If our number of fids and commands doesn't match, we should go back to the beginning.
  ##  We do this after drawing the blobs, and we sleep for a couple of seconds, so the
  ##  user can see which tiles weren't identified.
  if len(commandBlobs) != len(fidBlobs):
    lcdPort.write("|")
    lcdPort.write(chr(0))
    print "Did not find same number of fids and commands!"
    commandErrorString = "Found " + str(len(fidBlobs)) + " fids for " + str(len(commandBlobs)) + " commands"
    lcdPort.write(commandErrorString)
    i.save(displayWindow)
    time.sleep(5)
    return

  ## Create a list of commands. Each command will be based on the angle from
  ##  the center of a circle to the center of its corresponding command blob,
  ##  minus the train angle. We also draw a line from the center of each fid
  ##  to the center of each command, just for further verification.
  commandList = []
  ## Create a simpleCV drawing layer that we'll draw lines on. We'll apply it
  ##  later to put the lines in the image.
  commandAngleLines = DrawingLayer((i.width,i.height))
  cmdDistInvalid = False  ## we need to know that our fids and commands are
                          ##  not too far from one another. If this gets set,
                          ##  we'll bail and print an error
  ## Iterate across both fidBlobs and commandBlobs. By now, both lists should
  ##  be only objects which are close to each other, in order from closest to
  ##  start tile to furthest.
  for j in range(0, len(fidBlobs)):
    x1 = fidBlobs[j][2][0]
    y1 = fidBlobs[j][2][1]
    x2 = commandBlobs[j][2][0]
    y2 = commandBlobs[j][2][1]
    cmdDist = hypot(x2-x1, y2-y1)
    if cmdDist > 25:
      cmdDistInvalid = True
      return
    ## Draw the line from the fid to the command. That's easy.
    commandAngleLines.line(fidBlobs[j][2],commandBlobs[j][2], color = white, width = 1)
    ## atan2() is better about maintaining direction info than atan(). 
    localAngle = degrees(atan2(y2-y1,x2-x1))
    commandList.append(localAngle-trainAngle)

  ## If any of the fids were too far from their respective commands in the
  ##  sorted lists, we want to print an error message and bail.
  if cmdDistInvalid is True:
    lcdPort.write("|")
    lcdPort.write(chr(0))
    lcdPort.write("Commands and fids don't match!")
    print "Commands and fids don't match!"
    return
  ## Stick the drawing layer with the command angle lines onto the image, then
  ##  apply both it AND the layer with the line from the start tile to the last
  ##  fid to the image.
  i.addDrawingLayer(commandAngleLines)
  i.applyLayers()

  ## Now, parse out the commands which are implied by the angles we just calculated.
  print "Command angles:"
  commandText = []
  for item in commandList:
    commandText.append(str(extractCommand(item))[0])
    
  ## Dump out the commands across the serial port.
  for command in commandText:
    myPort.write(command)
    lcdPort.write(command)
    lcdPort.write(" ")
  myPort.write("x")
  
  ## Print a done message, then we go back to the top and wait for next button press.
  print "All done!"
  lcdPort.write("\n\rAll done!")
  
  ## Show the image in all its marked-up glory.
  i.save(displayWindow) 
  time.sleep(3.0)
  
  ## Close the display window, to try and plug the memory leak that exists in
  ##  pygame, somewhere.
  displayWindow.quit()
  return 0
  
displayWindow = Display(resolution = displayResolution)
  
## Most of the time, we'll just hang out in this loop, exiting only
##  on demand.
while TRUE:
  
  ## We're going to use a small LCD as the main feedback UI, so we can use the
  ##  entire monitor to display the visuals of what we're doing.
  ##  Initialize it.
  lcdPort.write("|")
  lcdPort.write(chr(0))
  lcdPort.write("Ready to play!")
  ## There's a bug, somewhere, in the display functionality of SimpleCV which
  ##  precludes the display of images in a running frame-by-frame manner. After
  ##  some period of time something happens which, in my system, results in the
  ##  OS simply logging me out. To cope with this, we're going to live update
  ##  the image
  imageDisplays = 0
  
  ## Check to see if a button connected to GPIO2 is pressed or not. The pin
  ##  will be set up such that when the button is pressed, the pin will be low.
  ##  While we're waiting, continuously display a grayscale version of an image
  ##  from the camera.
  while '0' not in buttonCheck(2):
    imageDisplays = imageDisplays + 1
    if imageDisplays < 100:
      i = cam.getImage().grayscale()
      i.save(displayWindow)
    else:
      displayWindow.quit()
      displayWindow = Display(resolution = displayResolution)
      imageDisplays = 0
    if '0' in buttonCheck(3):
      sys.exit(1)
      
  processImage()
  displayWindow = Display(resolution = displayResolution)