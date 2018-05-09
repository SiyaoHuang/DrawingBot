import pmap
from pmap import *
from wireless import *
from imageprocessor import *
import time

IP_ADDR = '192.168.43.28'
PORT = 5005

# This class provides high level actions of the robot, primarily 
# going towards a target point. It uses the image processor in
# conjunction with the pmap class to find the robot's location 
# and control the robot accordingly. It also performs the 
# calibrations necessary to configure the pmap surface normal.
class Controller(object):
	def __init__(self, epsxy=1, epst=0.1):
		self.imageprocessor = ImageProcessor()
		self.bot = VirtualBotTX(IP_ADDR, PORT)
		self.pmap = PMap(epsx=0.0001, epsy=0.01)
		self.position = None
		self.direction = None
		self.epsxy = epsxy
		self.epst = epst
		self.rspeed = 0.3
		self.fspeed = 0.3
		self.pspeed = 0.1

	# Determines the plane of the paper in 3D space
	def calibrate(self):
		print "Establishing start position..."
		start = self.imageprocessor.getPoints()
		while start == None:
			start = self.imageprocessor.getPoints()
		p1i, p2i, p3i = start
		print start

		# Calibrate surface normal
		print "Calibrating surface normal..."
		
		self.bot.forward(self.fspeed)
		curr = start
		while max(curr, key=lambda x: x[1])[1] > 0.35 * pmap.IMG_HEIGHT:
			curr = self.imageprocessor.getPoints()
			while curr == None:
				curr = self.imageprocessor.getPoints()

			p1, p2, p3 = curr
			self.pmap.addCalibration(p1, p2, p3)

		self.bot.rotate(self.rspeed)
		time.sleep(1.2)
		self.bot.forward(self.fspeed)
		while max(curr, key=lambda x: x[0])[0] < 0.60 * pmap.IMG_WIDTH:
			curr = self.imageprocessor.getPoints()
			while curr == None:
				curr = self.imageprocessor.getPoints()

			p1, p2, p3 = curr
			self.pmap.addCalibration(p1, p2, p3)
		self.bot.stop()

		# Set surface normal
		self.pmap.calibrateSurfaceNormal()
		self.pmap.initSurface(p1i, p2i, p3i)
		print self.pmap.surfaceNormal

		# Set starting position
		self.position, self.direction = self.pmap.surfaceMap(p1i, p2i, p3i)

		print "Finished!"

	# Sets up the PMap module by determining the surface normal
	# and sets the initial position and direction of the bot.
	# Calibrate without the bot.
	def calibrateManual(self):
		# Get start position
		start = self.imageprocessor.getPoints()
		while start == None:
			start = self.imageprocessor.getPoints()
		p1i, p2i, p3i = start

		# Calibrate PMap by providing a sample of coordinates
		ts = time.time()
		while time.time() - ts < 10:
			pos = self.imageprocessor.getPoints()
			if pos == None:
				continue
			p1, p2, p3 = pos
			self.pmap.addCalibration(p1, p2, p3)
			time.sleep(.05)
			
		# Set surface normal
		self.pmap.calibrateSurfaceNormal()
		self.pmap.initSurface(p1i, p2i, p3i)

		# Set position and direction of the bot
		self.position, self.direction = self.pmap.surfaceMap(p1i, p2i, p3i)

	# Continually prints out the 2D position of the bot on the surface.
	def printVector(self):
		while True:
			points = self.imageprocessor.getPoints()
			if points == None:
				continue
			p1, p2, p3 = points
			pos, d = self.pmap.surfaceMapFast(p1, p2, p3)
			print "(%f, %f)" % (pos.x, pos.y), "(%f, %f)" % (d.x, d.y)

	# Sets the 2D position and direction of the robot.
	def setVector(self):
		start = self.imageprocessor.getPoints()
		while start == None:
			start = self.imageprocessor.getPoints()
		p1i, p2i, p3i = start
		self.position, self.direction = self.pmap.surfaceMapFast(p1i, p2i, p3i)

	# Moves the bot to a certain target coordinate until it is within
	# a distance of self.epsxy.
	def gotoTarget(self, target, draw=False):
		# Rotate bot towards the target
		self.setVector()
		targetDirection = (target - self.position).normalize()
		self.bot.rotate(-self.rspeed)
		print "dir error:"
		while abs(1 - self.direction * targetDirection) > self.epst:
			self.setVector()
			print abs(1 - self.direction * targetDirection)

		# Put pen down
		if draw:
			self.bot.penDown(self.pspeed)

		# Move towards target point
		self.bot.stop()
		self.bot.forward(self.fspeed)
		while self.position.dist_to(target) > self.epsxy:
			# Get direction vector to target
			self.setVector()
			targetDirection = (target - self.position).normalize()
			tvec = Vec3(targetDirection.x, targetDirection.y, 0.0).normalize()
			cvec = Vec3(self.direction.x, self.direction.y, 0.0).normalize()

			# Calculate error
			sign = 1 if cvec.cross(tvec).z > 0 else -1
			err = sign * (1 - tvec * cvec)
			print err
			scale = 100000

			# Adjust trajectory based on error
			self.bot.adjust(scale * err)
			
		if draw:
			self.bot.penUp(self.pspeed)
		self.bot.stop()