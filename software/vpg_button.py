##############################################################################
# gpio_test.py
#
# Example code for GPIO access on the pcDuino via Python
#
# 26 Mar 2013 - Mike Hord, SparkFun Electronics
#
# This code is beerware- if you find it useful, please buy me (or, for that
# matter, any other SparkFun employee you met) a pint next time you meet us at
# the local.
#
##############################################################################

#!/usr/bin/env python

import time, os

def buttonCheck(buttonID):
  ## For simplicity's sake, we'll create a string for our paths.
  GPIO_MODE_PATH= os.path.normpath('/sys/devices/virtual/misc/gpio/mode/')
  GPIO_PIN_PATH=os.path.normpath('/sys/devices/virtual/misc/gpio/pin/')

  ## Create a few strings for file I/O equivalence
  HIGH = "1"
  LOW =  "0"
  INPUT = "0"
  OUTPUT = "1"
  INPUT_PU = "8"

  pin = os.path.join(GPIO_PIN_PATH, 'gpio'+str(buttonID))
  mode = os.path.join(GPIO_MODE_PATH, 'gpio'+str(buttonID))

  file = open(mode, 'r+') ## open the file in r/w mode
  file.write(INPUT_PU)    ## set the mode of the pin
  file.close()            ## IMPORTANT- must close file to make changes!

  temp = ['']             ## a string to store the value 
  file = open(pin, 'r')   ## open the file
  temp[0] = file.read()   ## fetch the pin state

  file.close()  ## Make sure to close the file when you're done!
  
  return temp[0]
