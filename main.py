import controller.Controller as Controller

# draw stuff on piTFT maybe?

# read in points as array
pointArray = []
controller = Controller()
print "starting drawing."

for i in pointArray:
	print "drawing point " + str(i)
	controller.gotoTarget(i)

print "done."