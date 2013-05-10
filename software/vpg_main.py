from SimpleCV import *

cam = Camera()

i = cam.getImage()
i = cam.getImage()
i = cam.getImage().grayscale()

i.show()

## The first thing to do is identify the location of the "Start" tile. This
##   tile has a large white blob, 20mm square. We can use that fact to
##   determine three things: pixel size in the FOV, angle of the tile train,
##   and the center of the start tile.
##   Those three facts let us guess at where the next instruction tiles will 
##   be, and exclude objects that are not where we want them to be.
## The settings for this have been experimentally determined to work. YMMV, if
##   you're not me.
blobList = i.findBlobs(threshval = 125, minsize = 2000, maxsize = 3000)

## If we don't find a blob, it's probably because there's no start tile. Call
##   an error and punch out!
if blobList is None:
  print "No start tile found!"
  sys.exit()

## Otherwise, we'll want to figure out a few things: the angle of the train,
##   the center of the start tile, and the pixel size, in mm.
elif blobList is not None:
  blobList[0].draw()
  trainAngle = blobList[0].angle()
  startTileCenter = blobList[0].centroid()
  startTileYSize = blobList[0].minRectHeight()
  startTileXSize = blobList[0].minRectWidth()
  pixelSize = 20 / ((ySize + xSize)/2)