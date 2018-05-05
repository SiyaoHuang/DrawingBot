from controller import *
import time

# Read in points as array
pointArray = []

# Create controller and set it up
##controller = Controller()
##controller.imageprocessor.write = False
##print "calibrating..."
##controller.calibrate()
##print "finished!"
##print controller.pmap.surfaceNormal
##controller.printVector()

bot = Bot()
bot.forward(0.2)

##time.sleep(1)
##bot.adjust(.1)
##time.sleep(1)
##bot.adjust(-.1)
while True:
    pass

for i in pointArray:
	print "drawing point " + str(i)
	controller.gotoTarget(i)

print "done."