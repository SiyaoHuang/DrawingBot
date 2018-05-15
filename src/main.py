from controller import *
import time
import sys

c = Controller()
sys.exit(0)
# Move towards target point
print 'calibrating...'
c.calibrateManual()

starttime = time.time()
target = Vec2(0.0, 0.0)
c.bot.forward(c.fspeed)
c.P = 50000
while True:
			# Get direction vector to target
			c.setVector()
			targetDirection = (target - c.position).normalize()
			
			# Calculate error
			angle = math.acos(targetDirection * c.direction)
			sign = 1 if targetDirection.cross(c.direction) < 0 else -1
			scale = c.P #14000
			att = c.position.dist_to(target)

			# Adjust trajectory based on error
			print sign * scale * angle
			c.bot.adjust(sign * scale * angle)
sys.exit(0)
##p = pmap.PMap(epsx=0.0001, epsy=0.01)
##points = p.mapPicture([
##	(72, 146),
##	(69, 45),
##	(212, 43),
##	(215, 137),
##	(72, 146)
##])
##
##for i in points:
##	print i
##sys.exit(0)

star = [
	(0.7,  0.0),
	(2.0, -4.0),
	(3.3,  0.0),
	(0.0, -2.3),
	(4.0, -2.3),
	(0.7,  0.0)
]

box = [
	Vec2(0.0,  0.0),
	Vec2(4.0,  0.0),
	Vec2(4.0, -4.0),
	Vec2(0.0, -4.0),
	Vec2(0.0,  0.0)
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
c.drawPoints(box)
