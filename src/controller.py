import pmap
from pmap import *
import wireless
from wireless import *
from imageprocessor import *
import time
import math

IP_ADDR = '192.168.43.28'
PORT = 5005

# This class provides high level actions of the robot, primarily 
# going towards a target point. It uses the image processor in
# conjunction with the pmap class to find the robot's location 
# and control the robot accordingly. It also performs the 
# calibrations necessary to configure the pmap surface normal.
class Controller(object):
	def __init__(self, epsxy=0.5, epst=2):
		self.imageprocessor = ImageProcessor()
		self.bot = VirtualBotTX()
		self.pmap = PMap(epsx=0.0001, epsy=0.01)

		# Position fields
		self.position = None
		self.direction = None
		self.epsxy = epsxy
		self.epst = epst * 2 * 3.141592 / 360

		# Bot fields
		self.rspeed = -0.2
		self.raspeed = -0.35
		self.fspeed = 0.4
		self.pspeed = 0.1
		self.upspeed = 0.15
		self.dnspeed = -0.15
		self.rtrim = -0.095
		self.ltrim = 0

		self.setupBot()

	def setupBot(self):
		self.bot.trimRight(self.rtrim)
		self.bot.trimLeft(self.ltrim)

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
		
		def inBoundary(points):
			x, y = points[1]
			framex, framey = 0.15, 0.15
			top = y > framey * pmap.IMG_HEIGHT
			bottom = y < (1 - framey) * pmap.IMG_HEIGHT
			left = x > framex * pmap.IMG_WIDTH
			right = x < (1 - framex) * pmap.IMG_WIDTH
			return top and bottom and left and right

		# Hit the boundary 5 times
		hit = 0
		while hit < 5:

			# Get points
			points = self.imageprocessor.getPoints()
			while points == None:
				points = self.imageprocessor.getPoints()

			# Keep going forward until a boundary is hit
			self.bot.forward(self.fspeed)
			time.sleep(1)
			while inBoundary(points):
				p1, p2, p3 = points
				self.pmap.addCalibration(p1, p2, p3)
				points = self.imageprocessor.getPoints()
				while points == None:
					points = self.imageprocessor.getPoints()

			# Rotate for some time
			self.bot.rotate(-self.rspeed)
			time.sleep(1)

			hit += 1

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
		self.bot.rotate(self.rspeed)
		while math.acos(self.direction * targetDirection) > 30 * 2 * 3.141592 / 360:
			self.setVector()
			targetDirection = (target - self.position).normalize()

		# Rotate in small steps
		while targetDirection.cross(self.direction) > 0:
			self.bot.rotateAdjust(self.raspeed)
			time.sleep(.25)
			self.setVector()
			targetDirection = (target - self.position).normalize()
			print "Cross product:", targetDirection.cross(self.direction)

		# Put pen down or up
		if draw and not self.bot.pen:
			self.bot.penDown(self.dnspeed)
			time.sleep(1.5)
		elif not draw and self.bot.pen:
			self.bot.penUp(self.upspeed)
			time.sleep(1.5)

		# Move towards target point
		self.bot.forward(self.fspeed)
		while self.position.dist_to(target) > self.epsxy * 3.5:

			# Get direction vector to target
			self.setVector()
			targetDirection = (target - self.position).normalize()
			tvec = Vec3(targetDirection.x, targetDirection.y, 0.0).normalize()
			cvec = Vec3(self.direction.x, self.direction.y, 0.0).normalize()
			
			# Calculate error
			dot = tvec * cvec
			self.setVector()
			sign = 1 if cvec.cross(tvec).z > 0 else -1
			err = sign * (1 - dot)
			scale = 32000
			att = min(self.position.dist_to(target), 4)

			# Adjust trajectory based on error
			self.bot.adjust(scale * att * err)
		
		# Move towards target in small increments until just passed
		while targetDirection * self.direction > 0:
			self.bot.forwardAdjust(self.fspeed)
			time.sleep(0.25)
			self.setVector()
			targetDirection = (target - self.position).normalize()
			print "Dot product:", targetDirection * self.direction
		
		self.bot.stop()