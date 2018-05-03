from controller import *

# Read in points as array
pointArray = []

# Create controller and set it up
controller = Controller()
controller.imageprocessor.write = True
print "calibrating..."
controller.calibrateManual()
print "finished!"
print controller.pmap.surfaceNormal

for i in pointArray:
	print "drawing point " + str(i)
	controller.gotoTarget(i)

print "done."