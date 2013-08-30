FORWARD  = 0
RIGHT45  = 1
RIGHT90  = 2
RIGHT135 = 3
REV      = 4
LEFT45   = 7
LEFT90   = 6
LEFT135  = 5

import os

def setSerPins():
    ## For simplicity's sake, we'll create a string for our paths.
  GPIO_MODE_PATH= os.path.normpath('/sys/devices/virtual/misc/gpio/mode/')
  GPIO_PIN_PATH=os.path.normpath('/sys/devices/virtual/misc/gpio/pin/')

  ## Create a few strings for file I/O equivalence
  HIGH = "1"
  LOW =  "0"
  INPUT = "0"
  OUTPUT = "1"
  SERIAL = "3"
  INPUT_PU = "8"

  ## First, populate the arrays with file objects that we can use later.
  for pinID in range(0,2):
    pin = os.path.join(GPIO_PIN_PATH, 'gpio'+str(pinID))
    mode = os.path.join(GPIO_MODE_PATH, 'gpio'+str(pinID))

    file = open(mode, 'rb+') ## open the file in r/w mode
    file.write('3')           ## set the mode of the pin
    file.close()            ## IMPORTANT- must close file to make changes!

    temp = ['']             ## a string to store the value 
    file = open(pin, 'r')   ## open the file
    temp[0] = file.read()   ## fetch the pin state

    file.close()  ## Make sure to close the file when you're done!
  
def extractCommand(angle):
  if angle < 0:
    angle = angle+360
  angle = round(angle/45, 0)
  if angle > 7.0:
    angle = 0.0
  print angle
  return angle
  