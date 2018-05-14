from controller import *
import time
import sys

star = [
	(0.7,  0.0),
	(2.0, -4.0),
	(3.3,  0.0),
	(0.0, -2.3),
	(4.0, -2.3),
	(0.7,  0.0)
]

box = [
	(0.0,  0.0),
	(4.0,  0.0),
	(4.0, -4.0),
	(0.0, -4.0),
	(0.0,  0.0)
]

line = [
	(0.0,  0.0),
	(0.0, -5.0),
	(0.0,  0.0),
	(0.0, -5.0),
	(0.0,  0.0),
	(0.0, -5.0),
]

c = Controller()
c.calibrate()
points = c.pmap.mapPicture([
	(72, 146),
	(69, 45),
	(212, 43),
	(215, 137),
	(72, 146)
])

for i in points:
	print i

#c.drawPoints(box)
