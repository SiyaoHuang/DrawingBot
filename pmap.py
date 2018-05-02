from pmath import *

# constants
TRIANGLE_UNITS	= 1.0
DISTANCE_TO_CAM = 11.0 / TRIANGLE_UNITS
P2U				= 8.5 / 526.6925099144661
DISTANCE_MAX	= 100.0
IMG_WIDTH		= 832
IMG_HEIGHT		= 624

class Triangle(object):
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b

	def center(self):
		avg = (self.r + self.g + self.b) / 3.0
		return TRIANGLE_UNITS * avg

	def normal(self):
		return (self.b - self.r).cross(self.g - self.r).normalize()

class PMap(object):
	def __init__(self, epsx, epsy):
		self.epsx = epsx
		self.epsy = epsy
		self.ra = None
		self.rb = None
		self.rc = None
		self.start = None
		self.surfaceNormal = None #Vec3(0.039564, -0.737417, 0.674278)
		self.calibrate = []

	# Input vectors in pixel coordinates
	def setPoints(self, p1, p2, p3):
		p1x, p1y = p1
		p2x, p2y = p2
		p3x, p3y = p3

		# Transform pixel coordinates to be centered at the origin
		p1x, p1y = p1x - float(IMG_WIDTH / 2), float(IMG_HEIGHT / 2) - p1y
		p2x, p2y = p2x - float(IMG_WIDTH / 2), float(IMG_HEIGHT / 2) - p2y
		p3x, p3y = p3x - float(IMG_WIDTH / 2), float(IMG_HEIGHT / 2) - p3y

		# Convert pixels to units and set z coordinate
		p1 = P2U * Vec3(p1x, p1y, 0.0)
		p2 = P2U * Vec3(p2x, p2y, 0.0)
		p3 = P2U * Vec3(p3x, p3y, 0.0)
		p1.z = DISTANCE_TO_CAM
		p2.z = DISTANCE_TO_CAM
		p3.z = DISTANCE_TO_CAM

		# Normalize and use as direction vectors
		self.ra = p1.normalize()
		self.rb = p2.normalize()
		self.rc = p3.normalize()

		print self.ra

	# Traces out a triangle for a given ta value and returns
	# the path that it took.
	def generateDiff(self, t):
		def genHelper(t, i, path):
			if i == 3:
				return [path + [t]]
			if t == None:
				return genHelper(None, i + 1, path + [None]) + genHelper(None, i + 1, path + [None])

			rab = self.ra * self.rb
			rcb = self.rc * self.rb
			rac = self.ra * self.rc
			arr = [rab, rcb, rac]
			left = t * arr[i]
			right = t * t * (arr[i] * arr[i] - 1) + 1

			if right < 0:
				return genHelper(None, i + 1, path + [None]) + genHelper(None, i + 1, path + [None])

			plus = left + right ** .5
			minus = left - right ** .5
			return genHelper(plus, i + 1, path + [t]) + genHelper(minus, i + 1, path + [t])
		return genHelper(t, 0, [])

	# Returns a function that traces a specific triangle path and returns 
	# an array containing the path that it took.
	def makeTraceFunc(self, path):
		return lambda t: self.generateDiff(t)[path]

	# Returns a function that traces a specific triangle path for a given
	# ta and returns abs(ta - looped around ta)
	def makeDiffFunc(self, path):
		def func(t):
			res = self.generateDiff(t)[path]
			if res[-1] == None:
				return None
			return abs(res[0] - res[-1])
		return func

	# Returns a function that traces a specific triangle path for a given
	# ta and returns ta - looped around ta
	def makeSDiffFunc(self, path):
		def func(t):
			res = self.generateDiff(t)[path]
			if res[-1] == None:
				return None
			return res[0] - res[-1]
		return func

	# Sweeps all diff function paths with a certain step size and prints out
	# the resulting values. Can copy/paste into excel to graph. 
	def sweepTriangles(self, step):
		funcs = []
		for i in range(8):
			funcs += [self.makeSDiffFunc(i)]
		
		i = 0
		s = ""
		while i < (1 - (self.ra * self.rb) ** 2) ** -.5:
			s2 = ""
			for f in funcs:
				res = f(i)
				s2 += str(' ' if res == None else res) + '\t'
			s += s2 + '\n'
			i += step
		print s

	# Finds possible triangles within an epsilon value and
	# returns array of corresponding ta, tb, and tc.
	def findTriangles(self):
		mins = []
		for i in range(8):
			f = self.makeDiffFunc(i)
			trace = self.makeTraceFunc(i)
			end = findEnd(f, 0.0, DISTANCE_MAX, self.epsx)
			m = findMin(f, 0.0, end, self.epsx)
			mins += [(f(m), trace(m))]

		mins = filter(lambda x: x[0] < self.epsy, mins)
		mins = map(lambda x: x[1], mins)
		triangles = []
		for tri in mins:
			r, g, b, r2 = tri
			r = (r + r2) / 2
			r, g, b = self.ra * r, self.rb * g, self.rc * b
			triangles += [Triangle(r, g, b)]
		return triangles

	# Finds triangle whose normal is closest to the established
	# surface normal.
	def getClosestTriangle(self, arr):
		return min(arr, key=lambda t: abs(1 - t.normal() * self.surfaceNormal))

	# Given a list of triangles, finds the surface normal that is 
	# closest to all triangle normals.
	def calibrateSurfaceNormal(self):
		arr = self.calibrate
		# TODO: find surface normal
		self.surfaceNormal = Vec3(0.0, 0.0, 0.0)

	# Adds possible triangles to the calibration
	def addCalibration(self, p1, p2, p3):
		self.setPoints(p1, p2, p3)
		self.calibrate += self.findTriangles()

	# Resets calibration array
	def resetCalibration(self):
		self.calibrate = []

	# Finds position in 3D space relative to the camera
	def perspectiveMap(self, p1, p2, p3):
		self.setPoints(p1, p2, p3)
		ts = self.findTriangles()
		return self.getClosestTriangle(ts).center()

	# Sets starting position in 3D space
	def setStartPosition(self, p1, p2, p3):
		self.start = self.perspectiveMap(p1, p2, p3)

	# Finds position on the surface plane relative to the starting position
	# and returns 2D coordinates
	def surfaceMap(self, p1, p2, p3):
		# TODO: map 3D point to 2D coordinate in plane space
		pass

p = PMap(epsx=0.001, epsy=0.01)
# print p.perspectiveMap((407, 218), (447, 273), (493, 220))
# p.setPoints((407, 218), (447, 273), (493, 220)) #<-0.013079, 0.136606, 0.990539>, 7.88
# p.setPoints((406, 330), (438, 370), (477, 333)) #<-0.014665, -0.026396, 0.999544>, 9.49
# p.sweepTriangles(0.01)

a = 7.88 * Vec3(-0.013079, 0.136606, 0.990539)
b = 9.49 * Vec3(-0.014665, -0.026396, 0.999544)
print (a - b).mag()
