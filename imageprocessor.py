import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import imutils

# Constants
YMIN, YMAX 			=  50,  70
GMIN, GMAX 			= 105, 130
BMIN, BMAX 			=  23,  40
SMIN, SMAX 			=  40, 255
VYMIN, VYMAX 		=   0, 255
VGMIN, VGMAX 		=   0, 255
VBMIN, VBMAX 		=  10, 255
SIZEMIN				=      900

RES 				= 832, 624
FRAMERATE 			=		30

class ImageProcessor(object):
	def __init__(self):
		self.cam = PiCamera()
		self.cam.resolution = RES
		self.cam.framerate = FRAMERATE
		self.raw = PiRGBArray(self.cam, size=RES)
		self.write = False

	# Takes an image and returns it as a numpy array.
	def getImage(self):
		self.cam.capture(self.raw, format='bgr', use_video_port=True)
		arr = self.raw.array
		self.raw.truncate(0)
		return arr

	# Returns number of pixels in the contour.
	def checkSize(self, c):
		return cv2.moments(c)['m00'] > SIZEMIN

	# Returns how close to a circle the contour is, with 0 being
	# a perfect circle.
	def getShape(self, c):
		m = cv2.moments(c)
		shapex = m['nu20']
		shapey = m['nu02']
		return shapex + shapey

	# Returns pixel coordinates of the center of the contour.
	def getCenter(self, c):
		m = cv2.moments(c)
		cx = int(m['m10']/m['m00'])
		cy = int(m['m01']/m['m00'])
		return (cx, cy)

	# Takes a picture and returns the pixel coordinates of the yellow, 
	# green, and blue circles respectively.
	def getPoints(self):
		# read in image and threshold
		imagergb = self.getImage()
		image = cv2.cvtColor(imagergb, cv2.COLOR_BGR2HSV)
		maskg = cv2.inRange(image, np.array([YMIN,SMIN,VYMIN]),np.array([YMAX,SMAX,VYMAX]))
		maskb = cv2.inRange(image, np.array([GMIN,SMIN,VGMIN]),np.array([GMAX,SMAX,VGMAX]))
		masky = cv2.inRange(image, np.array([BMIN,SMIN,VBMIN]),np.array([BMAX,SMAX,VBMAX]))

		if self.write:
			cv2.imwrite("imagergb.jpg",imagergb)
			cv2.imwrite("image.jpg",image)
			cv2.imwrite("masky.jpg",masky)
			cv2.imwrite("maskg.jpg",maskg)
			cv2.imwrite("maskb.jpg",maskb)

		# image processing to find center of yellow, green, and blue circles
		cntsy = cv2.findContours(masky.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsy = cntsy[0] if imutils.is_cv2() else cntsy[1]
		cntsy = filter(self.checkSize, cntsy)
		if cntsy == []:
			return None
		cntsy = min(cntsy, key=self.getShape)

		cntsg = cv2.findContours(maskg.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsg = cntsg[0] if imutils.is_cv2() else cntsg[1]
		cntsg = filter(self.checkSize, cntsg)
		if cntsg == []:
			return None
		cntsg = min(cntsg, key=self.getShape)

		cntsb = cv2.findContours(maskb.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsb = cntsb[0] if imutils.is_cv2() else cntsb[1]
		cntsb = filter(self.checkSize, cntsb)
		if cntsb == []:
			return None
		cntsb = min(cntsb, key=self.getShape)

		# get coordinates
		y, g, b = self.getCenter(cntsy), self.getCenter(cntsg), self.getCenter(cntsb)
		return y, g, b
