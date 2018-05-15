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
		self.epst = 45 * (2 * 3.141592 / 360)
		self.epss = 0.03

		# Calibrate fields
		self.framex = 0.20
		self.framey = 0.20
		self.calibrated = False
		self.P = 49200

		# Bot parameters
		self.rspeed = -0.2
		self.raspeed = -0.35
		self.fspeed = 0.35
		self.pspeed = 0.1
		self.upspeed = 0.2
		self.dnspeed = -0.2
		self.rtrim = -0.02
		self.ltrim = 0
		self.pdsleep = 0.4
		self.pusleep = 1
		self.setupBot()

	# Sets initial parameters of the bot
	def setupBot(self):
		self.bot.trimRight(self.rtrim)
		self.bot.trimLeft(self.ltrim)
		self.bot.penDownSleep(self.pdsleep)
		self.bot.penUpSleep(self.pusleep)
		self.bot.penDown(self.dnspeed)
		self.bot.penUp(self.upspeed)
	
	def calibrateRoutine(self):
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
		
		# move in a box
		for i in range(8):
			self.bot.forward(self.fspeed)
			starttime = time.time()
			while time.time() - starttime < 1.1:
				points = self.imageprocessor.getPoints()
				if points != None:
					p1, p2, p3 = points
					self.pmap.addCalibration(p1, p2, p3)

			self.bot.rotate(-self.rspeed)
			time.sleep(0.8)
		self.bot.stop()

		# Set surface normal
		self.pmap.calibrateSurfaceNormal()
		self.pmap.initSurface(p1i, p2i, p3i)
		print self.pmap.surfaceNormal

		# Set starting position
		self.position, self.direction = self.pmap.surfaceMap(p1i, p2i, p3i)
		self.calibrated = True

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
			starttime = time.time()
			while time.time() - starttime < 0.9 or inBoundary(points):
				p1, p2, p3 = points
				self.pmap.addCalibration(p1, p2, p3)
				points = self.imageprocessor.getPoints()
				while points == None:
					points = self.imageprocessor.getPoints()

			# Rotate for some time
			self.bot.rotate(-self.rspeed)
			starttime = time.time()
			while time.time() - starttime < 1:
				p1, p2, p3 = points
				self.pmap.addCalibration(p1, p2, p3)
				points = self.imageprocessor.getPoints()
				while points == None:
					points = self.imageprocessor.getPoints()

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
		while math.acos(self.direction * targetDirection) > self.epst or targetDirection.cross(self.direction) < 0:
			self.bot.rotate(self.rspeed)
			self.setVector()
			targetDirection = (target - self.position).normalize()

		# Rotate in small steps until just passed
		while targetDirection.cross(self.direction) > self.epss:
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
		flag = False
		while self.position.dist_to(target) > self.epsxy:
			if not flag:
				self.bot.forward(self.fspeed)
				flag = True

			# Get direction vector to target
			self.setVector()
			targetDirection = (target - self.position).normalize()
			
			# Calculate error
			angle = math.acos(targetDirection * self.direction)
			sign = 1 if targetDirection.cross(self.direction) < 0 else -1
			scale = self.P
			att = self.position.dist_to(target)

			# Adjust trajectory based on error
			self.bot.adjust(sign * scale * angle)

		# Move towards target in small increments until just passed
		while targetDirection * self.direction > 0:
			self.bot.forwardAdjust(self.fspeed)
			self.setVector()
			targetDirection = (target - self.position).normalize()
			print "Position error:", targetDirection * self.direction
		
		self.bot.stop()

	def drawPoints(self, points):
		# Calibrate pmap for the surface normal
		self.calibrateRoutine()
		
		# Convert points
		points = self.pmap.mapPicture(points)

		# Draw points one by one
		self.gotoTarget(points[0])
		self.gotoTarget(points[0])
		for i in range(1, len(points)):
			self.gotoTarget(points[i], draw=True)
		
		# Put the pen back up
		self.bot.penUp(self.upspeed)