#from controller import *
import pmap
import time
import sys

p = pmap.PMap(epsx=0.0001, epsy=0.01)
points = p.mapPicture([
	(72, 146),
	(69, 45),
	(212, 43),
	(215, 137),
	(72, 146)
])

for i in points:
	print i
sys.exit(0)

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

for i in points:
	print i
c.drawPoints(box)
