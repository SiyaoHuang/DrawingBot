import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import imutils

# Constants
YMIN, YMAX 			=  23,  40
GMIN, GMAX 			=  45,  80
BMIN, BMAX 			=  100, 120
SMIN, SMAX 			=  30, 255
VYMIN, VYMAX 		=   0, 255
VGMIN, VGMAX 		=   0, 255
VBMIN, VBMAX 		=  0, 255
SIZEMIN				=      20 * 15
SIZEMAX = 70*60

RES 				= 832, 624
FRAMERATE 			=		30

# This class handles all image processing including taking a picture
# with the Raspberry Pi camera as well as performing the image processing 
# necessary to locate the centers of the yellow, green, and blue circles.
class ImageProcessor(object):
	def __init__(self):
		self.cam = PiCamera()
		self.cam.resolution = RES
		self.cam.framerate = FRAMERATE
		self.raw = PiRGBArray(self.cam, size=RES)
		self.write = False
		
		self.counter = 0

	# Takes an image and returns it as a numpy array.
	def getImage(self):
		self.cam.capture(self.raw, format='bgr', use_video_port=True)
		arr = self.raw.array
		self.raw.truncate(0)
		return arr

	# Returns number of pixels in the contour.
	def checkSize(self, c):
		return SIZEMAX > cv2.moments(c)['m00'] > SIZEMIN and self.getShape(c) < 0.5

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
	
	def pixelDistance(self, a, b):
		return ((float(a[0]) - b[0]) ** 2 + (float(a[1]) - b[1]) ** 2) ** .5

	# Takes a picture and returns the pixel coordinates of the yellow, 
	# green, and blue circles respectively. Returns None if it is unable 
	# to find one or more of the circles.
	def getPoints(self):
		# read in image and threshold to get binary images
		imagergb = self.getImage()
		image = cv2.cvtColor(imagergb, cv2.COLOR_BGR2HSV)
		masky = cv2.inRange(image, np.array([YMIN,SMIN,VYMIN]),np.array([YMAX,SMAX,VYMAX]))
		maskg = cv2.inRange(image, np.array([GMIN,SMIN,VGMIN]),np.array([GMAX,SMAX,VGMAX]))
		maskb = cv2.inRange(image, np.array([BMIN,70,VBMIN]),np.array([BMAX,SMAX,VBMAX]))

		# image processing to find center of yellow, green, and blue circles
		cntsy = cv2.findContours(masky.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsy = cntsy[0] if imutils.is_cv2() else cntsy[1]
		cntsy = filter(self.checkSize, cntsy)
		if cntsy == []:
			return None
		cntsy = sorted(cntsy, key=self.getShape)

		cntsg = cv2.findContours(maskg.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsg = cntsg[0] if imutils.is_cv2() else cntsg[1]
		cntsg = filter(self.checkSize, cntsg)
		if cntsg == []:
			return None
		cntsg = sorted(cntsg, key=self.getShape)

		cntsb = cv2.findContours(maskb.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsb = cntsb[0] if imutils.is_cv2() else cntsb[1]
		cntsb = filter(self.checkSize, cntsb)
		if cntsb == []:
			return None
		cntsb = sorted(cntsb, key=self.getShape)
		
		if len(cntsy) == 0 or len(cntsg) == 0 or len(cntsb) == 0:
                    return None
                
                # Compare distances
                m = 2 * self.pixelDistance((0, 0), RES)
                triple = None
                for i in cntsy[:3]:
                    for j in cntsg[:3]:
                        for k in cntsb[:3]:
                            ic = self.getCenter(i)
                            jc = self.getCenter(j)
                            kc = self.getCenter(k)
                            ij = self.pixelDistance(ic, jc)
                            jk = self.pixelDistance(jc, kc)
                            ki = self.pixelDistance(kc, ic)
                            if ij + jk + ki < m:
                                m = ij + jk + ki
                                triple = (ic, jc, kc)
                
                y, g, b = triple
                if self.write:
                        imagergb = imagergb.copy()
                        imagergb[y[1]][y[0]] = [0, 0, 255]
                        imagergb[g[1]][g[0]] = [0, 0, 255]
                        imagergb[b[1]][b[0]] = [0, 0, 255]
			cv2.imwrite("output/imagergb%i.jpg" % self.counter,imagergb)
			cv2.imwrite("output/image%i.jpg" % self.counter,image)
			cv2.imwrite("output/masky%i.jpg" % self.counter,masky)
			cv2.imwrite("output/maskg%i.jpg" % self.counter,maskg)
			cv2.imwrite("output/maskb%i.jpg" % self.counter,maskb)
                        self.counter += 1

		return triple
