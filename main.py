from controller import *

# Read in points as array
pointArray = []

# Create controller and set it up
controller = Controller()
print "calibrating..."
controller.calibrate()
print "finished!"
controller.printPosition()

for i in pointArray:
	print "drawing point " + str(i)
	controller.gotoTarget(i)

print "done."