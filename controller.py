from pmap import *
from bot import *
from imageprocessor import *
import time

class Controller(object):
	def __init__(self, eps=0.1):
		self.imageprocessor = ImageProcessor()
		#self.bot = Bot()
		self.pmap = PMap(epsx=0.001, epsy=0.01)
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
	
	def calibrate(self):
                start = self.imageprocessor.getPoints()
                ts = time.time()
                while time.time() - ts < 10:
                        print time.time() - ts
                        p1, p2, p3 = self.imageprocessor.getPoints()
                        self.pmap.addCalibration(p1, p2, p3)
                        time.sleep(.2)
                self.pmap.calibrateSurfaceNormal()
                p1, p2, p3 = start
                self.pmap.setStartPosition(p1, p2, p3)

	def gotoTarget(self, target):
		# Moves the robot to the target point and stops
		while True:
			p1, p2, p3 = self.imageprocessor.getPoints()
			pos = self.pmap.perspectiveMap(p1, p2, p3)

Controller().calibrate()