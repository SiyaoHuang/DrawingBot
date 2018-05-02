from pmap import *
from bot import *
from imageprocessor import *
import time

class Controller(object):
	def __init__(self, eps=0.1):
		self.imageprocessor = ImageProcessor()
		self.bot = Bot()
		self.pmap = PMap(epsx=0.001, epsy=0.01)
		self.position = None
		self.direction = None
		self.eps = eps

	# Determines the plane of the paper in 3D space
##	def calibrate(self):
##		start = self.imageprocessor.getPoints()
##
##		# Calibrate surface normal
##		self.bot.forward(0.5)
##		curr = start
##		while max(curr, key=lambda x: x[1])[1] < pmap.IMG_HEIGHT / 2:
##			curr = p1, p2, p3 = self.imageprocessor.getPoints()
##			self.pmap.addCalibration(p1, p2, p3)
##		self.pmap.calibrateSurfaceNormal()
##
##		# Go back to starting position
##		p1, p2, p3 = start
##		self.pmap.setStartPosition(p1, p2, p3)
##		start = self.pmap.surfaceMap(p1, p2, p3)
##		self.gotoTarget(start)
	
	# Sets up the PMap module by determining the surface normal
	# and sets the initial position and direction of the bot.
	def calibrate(self):
		# Calibrate PMap by providing a sample of coordinates
		p1i, p2i, p3i = self.imageprocessor.getPoints()
		ts = time.time()
		while time.time() - ts < 10:
			pos = self.imageprocessor.getPoints()
			if pos == None:
				continue
			p1, p2, p3 = pos
			self.pmap.addCalibration(p1, p2, p3)
			time.sleep(.2)

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
		# Moves the robot to the target point and stops
		while True:
			p1, p2, p3 = self.imageprocessor.getPoints()
			pos, d = self.pmap.surfaceMap(p1, p2, p3)
