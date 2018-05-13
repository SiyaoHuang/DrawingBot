import pmap
from pmap import *
import wireless
import imageprocessor
import time
import math

# This class provides high level actions of the robot, primarily 
# going towards a target point. It uses the image processor in
# conjunction with the pmap class to find the robot's location 
# and control the robot accordingly. It also performs the 
# calibrations necessary to configure the pmap surface normal.
class Controller(object):
	def __init__(self):
		# Main components
		self.imageprocessor = imageprocessor.ImageProcessor()
		self.bot = wireless.VirtualBotTX()
		self.pmap = pmap.PMap(epsx=0.0001, epsy=0.01)

		# Position fields
		self.position = None
		self.direction = None
		self.epsxy = 1.75
		self.epst = 30 * (2 * 3.141592 / 360)

		# Calibrate fields
		self.framex = 0.15
		self.framey = 0.15
		self.calibrated = False

		# Bot parameters
		self.rspeed = -0.2
		self.raspeed = -0.35
		self.fspeed = 0.4
		self.pspeed = 0.1
		self.upspeed = 0.15
		self.dnspeed = -0.15
		self.rtrim = -0.095
		self.ltrim = 0
		self.pdsleep = 0.3
		self.pusleep = 0.62
		self.setupBot()

	# Sets initial parameters of the bot
	def setupBot(self):
		self.bot.trimRight(self.rtrim)
		self.bot.trimLeft(self.ltrim)
		self.bot.penDownSleep(self.pdsleep)
		self.bot.penUpSleep(self.pusleep)
		self.bot.penDown(self.dnspeed)
		self.bot.penUp(self.upspeed)

	# Determines the plane of the paper in 3D space
	def calibrate(self):
		if self.calibrated:
			print "Skipping calibration."
			return

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
			framex, framey = self.framex, self.framey
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
			time.sleep(1.5)

			hit += 1

		self.bot.stop()

		# Set surface normal
		self.pmap.calibrateSurfaceNormal()
		self.pmap.initSurface(p1i, p2i, p3i)
		print self.pmap.surfaceNormal

		# Set starting position
		self.position, self.direction = self.pmap.surfaceMap(p1i, p2i, p3i)
		self.calibrated = True

		print "Finished!"

	# Sets up the PMap module by determining the surface normal
	# and sets the initial position and direction of the bot.
	# Calibrate without the bot.
	def calibrateManual(self):
		if self.calibrated:
			print "Skipping calibration."
			return

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
			
		# Set surface normal
		self.pmap.calibrateSurfaceNormal()
		self.pmap.initSurface(p1i, p2i, p3i)

		# Set position and direction of the bot
		self.position, self.direction = self.pmap.surfaceMap(p1i, p2i, p3i)
		self.calibrated = True

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

	# Moves the bot to a certain target coordinate.
	def gotoTarget(self, target, draw=False):
		# Rotate bot towards the target
		self.setVector()
		targetDirection = (target - self.position).normalize()
		self.bot.rotate(self.rspeed)
		while math.acos(self.direction * targetDirection) > self.epst:
			self.setVector()
			targetDirection = (target - self.position).normalize()

		# Rotate in small steps until just passed
		while targetDirection.cross(self.direction) > 0:
			self.bot.rotateAdjust(self.raspeed)
			self.setVector()
			targetDirection = (target - self.position).normalize()
			print "Rotation error:", targetDirection.cross(self.direction)

		# Put pen down or up
		if draw and not self.bot.pen:
			self.bot.penDown(self.dnspeed)
		elif not draw and self.bot.pen:
			self.bot.penUp(self.upspeed)

		# Move towards target point
		self.bot.forward(self.fspeed)
		while self.position.dist_to(target) > self.epsxy:

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
			self.setVector()
			targetDirection = (target - self.position).normalize()
			print "Position error:", targetDirection * self.direction
		
		self.bot.stop()

	def drawPoints(self, points):
		# Calibrate pmap for the surface normal
		self.calibrate()

		# Draw points one by one
		self.gotoTarget(Vec2(0.0, 0.0))
		self.gotoTarget(Vec2(points[0][0], points[0][1]))
		for i in range(1, len(points)):
			self.gotoTarget(Vec2(points[i][0], points[i][1]), draw=True)
		self.gotoTarget(Vec2(0.0, 0.0))