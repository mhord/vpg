FORWARD  = 0
RIGHT45  = 1
RIGHT90  = 2
RIGHT135 = 3
REV      = 4
LEFT45   = 7
LEFT90   = 6
LEFT135  = 5

def extractCommand(angle):
  if angle < 0:
    angle = angle+360
  angle = round(angle/45, 0)
  if angle > 7.0:
    angle = 0.0
  print angle
  
