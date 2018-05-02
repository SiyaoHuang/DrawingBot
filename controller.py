from pmap import *
from bot import *
from imageprocessor import *
import time

# This class provides high level actions of the robot, primarily 
# going towards a target point. It uses the image processor in
# conjunction with the pmap class to find the robot's location 
# and control the robot accordingly. It also performs the 
# calibrations necessary to configure the pmap surface normal.
class Controller(object):
	def __init__(self, eps=0.1):
		self.imageprocessor = ImageProcessor()
		self.bot = Bot()
		self.pmap = PMap(epsx=0.001, epsy=0.01)
		self.position = None
		self.direction = None
		self.eps = eps

	# Determines the plane of the paper in 3D space
	def calibrate(self):
		start = self.imageprocessor.getPoints()
		while start != None:
			start = self.imageprocessor.getPoints()
		p1i, p2i, p3i = start

		# Calibrate surface normal
		self.bot.forward(0.5)
		curr = start
		while max(curr, key=lambda x: x[1])[1] < pmap.IMG_HEIGHT / 2:
			curr = self.imageprocessor.getPoints()
			if curr == None:
				continue

			p1, p2, p3 = curr
			self.pmap.addCalibration(p1, p2, p3)

		# Set surface normal
		self.pmap.calibrateSurfaceNormal()
		self.pmap.initSurface(p1i, p2i, p3i)

		# Go back to starting position
		while curr == None:
			curr = self.imageprocessor.getPoints()
		p1, p2, p3 = curr
		self.position, self.direction = self.pmap.surfaceMap(p1, p2, p3)

	# Sets up the PMap module by determining the surface normal
	# and sets the initial position and direction of the bot.
	# Calibrate without the bot.
	def calibrateManual(self):
		# Get start position
		start = self.imageprocessor.getPoints()
		while start != None:
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
			time.sleep(.1)

		# Set surface normal
		self.pmap.calibrateSurfaceNormal()
		self.pmap.initSurface(p1i, p2i, p3i)

		# Set position and direction of the bot
		self.position, self.direction = self.pmap.surfaceMap(p1i, p2i, p3i)

	# Continually prints out the 2D position of the bot on the surface.
	def printPosition(self):
		while True:
			p1, p2, p3 = self.imageprocessor.getPoints()
			pos, d = self.pmap.surfaceMap(p1, p2, p3)
			print str(pos), str(d)

	# Moves the bot to a certain target coordinate until it is within
	# a distance of self.eps.
	def gotoTarget(self, target):
		# TODO: implement PID possibly to guide robot to target
		pass
