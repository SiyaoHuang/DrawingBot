from controller import *

# Read in points as array
pointArray = []

# Create controller and set it up
##controller = Controller()
##controller.imageprocessor.write = False
##print "calibrating..."
##controller.calibrateManual()
##print "finished!"
##print controller.pmap.surfaceNormal
##controller.printVector()

bot = Bot()
bot.forward(.5)

while True:
    pass

for i in pointArray:
	print "drawing point " + str(i)
	controller.gotoTarget(i)

print "done."