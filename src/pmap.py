from pmath import *
import numpy as np
from numpy.linalg import inv

# constants
TRIANGLE_UNITS	= 1.0
DISTANCE_TO_CAM = 14.625
P2U				= 15.0 / 361.411
DISTANCE_MAX	= 100.0
IMG_WIDTH		= 416
IMG_HEIGHT		= 320
PIC_WIDTH       = 320
PIC_HEIGHT      = 240

class Triangle(object):
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b
		self.center = (r + g + b) / 3.0
		self.normal = (b - r).cross(g - r).normalize()
		self.direction = (g - (r + b) / 2).normalize()
	
	def __str__(self):
		return "[%s, %s]" % (str(self.center), str(self.normal))

# This class provides the functions necessary to convert screen space 
# coordinates (e.g. pixel coordinates) into coordinates in the 3D world as well as
# 2D coordinates on paper space (e.g. the plane on which the robot travels).
#
# Note: before perspective mapping can be utilized, the surface normal
# must be calibrated. This is done by:
# 	self.addCalibration -> ... -> self.addCalibration -> self.calibrateSurfaceNormal -> self.initSurface
class PMap(object):
	def __init__(self, epsx, epsy):
		# Epsilon values
		self.epsx = epsx
		self.epsy = epsy

		# Direction vectors
		self.ra = None
		self.rb = None
		self.rc = None

		# Surface variables
		self.calibrate = []
		self.start = None
		self.surfaceNormal = None
		self.surfaceX = None
		self.surfaceY = None
		self.framex = 0.15
		self.framey = 0.15

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
		f = lambda t: self.generateDiff(t)[path]
		return PFunction(f, self.epsx)

	# Returns a function that traces a specific triangle path for a given
	# ta and returns abs(ta - looped around ta)
	def makeDiffFunc(self, path):
		def f(t):
			res = self.generateDiff(t)[path]
			if res[-1] == None:
				return None
			return abs(res[0] - res[-1])
		return PFunction(f, self.epsx)

	# Returns a function that traces a specific triangle path for a given
	# ta and returns ta - looped around ta
	def makeSDiffFunc(self, path):
		def f(t):
			res = self.generateDiff(t)[path]
			if res[-1] == None:
				return None
			return res[0] - res[-1]
		return PFunction(f, self.epsx)

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
			end = f.findEnd(0.0, DISTANCE_MAX)
			m = f.findMin(0.0, end)
			if m == None:
				continue
			if None in trace(m):
				continue
			mins += [(f(m), trace(m))]

		mins = filter(lambda x: x[0] < self.epsy, mins)
		mins = map(lambda x: x[1], mins)
		triangles = []
		for tri in mins:
			r, g, b, _ = tri
			r, g, b = self.ra * r, self.rb * g, self.rc * b
			triangles += [Triangle(r, g, b)]
		return triangles

	# Finds triangle whose normal is closest to the established
	# surface normal.
	def getClosestTriangle(self, arr):
		return min(arr, key=lambda t: t.normal.dist_to(self.surfaceNormal))

	# Adds possible triangles to the calibration
	def addCalibration(self, p1, p2, p3):
		self.setPoints(p1, p2, p3)
		triangles = self.findTriangles()
		self.calibrate += triangles

	# Given a list of triangles, finds the surface normal that is 
	# closest to all triangle normals.
	def calibrateSurfaceNormal(self):
		bin1norm = None
		bin1pts = []
		bin2norm = None
		bin2pts = []
		for i in self.calibrate:
			if bin1norm == bin2norm == None:
				bin1norm = i.normal
				bin1pts += [i.center]
			elif bin2norm == None:
				bin2norm = i.normal
				bin2pts += [i.center]
			else:
				one = bin1norm.dist_to(i.normal)
				two = bin2norm.dist_to(i.normal)
				if one < two:
					bin1norm = (bin1norm + i.normal) / 2
					bin1pts += [i.center]
				else:
					bin2norm = (bin2norm + i.normal) / 2
					bin2pts += [i.center]

		bin1 = 0
		for i in range(len(bin1pts) - 1):
			bin1 += abs((bin1pts[i] - bin1pts[i + 1]) * bin1norm)
		bin2 = 0
		for i in range(len(bin2pts) - 1):
			bin2 += abs((bin2pts[i] - bin2pts[i + 1]) * bin2norm)

		self.surfaceNormal = bin1norm if bin1 < bin2 else bin2norm

	# Sets starting position in 3D space
	def initSurface(self, p1, p2, p3):
		triangle = self.perspectiveMap(p1, p2, p3)
		self.start = triangle.center
		self.surfaceX = triangle.direction.cross(self.surfaceNormal).normalize()
		self.surfaceY = self.surfaceNormal.cross(self.surfaceX).normalize()

	# Resets calibration array
	def resetCalibration(self):
		self.calibrate = []

	# Finds triangle in 3D space relative to the camera.
	def perspectiveMap(self, p1, p2, p3):
		self.setPoints(p1, p2, p3)
		ts = self.findTriangles()
		return self.getClosestTriangle(ts)

	# Finds position on the surface plane relative to the starting position
	# and returns 2D coordinates and the direction vector.
	def surfaceMap(self, p1, p2, p3):
		triangle = self.perspectiveMap(p1, p2, p3)
		p = triangle.center - self.start
		position = Vec2(self.surfaceX * p, self.surfaceY * p)
		d = triangle.direction
		direction = Vec2(self.surfaceX * d, self.surfaceY * d).normalize()
		return (position, direction)
	
	# Does the same thing as surfaceMap in O(1) time.
	def surfaceMapFast(self, p1, p2, p3):
		self.setPoints(p1, p2, p3)
		ramat = np.matrix([
			[self.surfaceX.x, self.surfaceY.x, -self.ra.x],
			[self.surfaceX.y, self.surfaceY.y, -self.ra.y],
			[self.surfaceX.z, self.surfaceY.z, -self.ra.z]
		])
		rbmat = np.matrix([
			[self.surfaceX.x, self.surfaceY.x, -self.rb.x],
			[self.surfaceX.y, self.surfaceY.y, -self.rb.y],
			[self.surfaceX.z, self.surfaceY.z, -self.rb.z]
		])
		rcmat = np.matrix([
			[self.surfaceX.x, self.surfaceY.x, -self.rc.x],
			[self.surfaceX.y, self.surfaceY.y, -self.rc.y],
			[self.surfaceX.z, self.surfaceY.z, -self.rc.z]
		])
		o = np.array([[self.start.x], [self.start.y], [self.start.z]])
		ra = ramat.I * o
		rb = rbmat.I * o
		rc = rcmat.I * o
		ra = Vec2(ra[0], ra[1])
		rb = Vec2(rb[0], rb[1])
		rc = Vec2(rc[0], rc[1])
		position = (ra + rb + rc) / 3
		direction = (rb - (ra + rc) / 2).normalize()
		return (position, direction)

	def surfaceMapSingle(self, p):
		px, py = p

		# Transform pixel coordinates to be centered at the origin
		px, py = px - float(IMG_WIDTH / 2), float(IMG_HEIGHT / 2) - py

		# Convert pixels to units and set z coordinate
		p = P2U * Vec3(px, py, 0.0)
		p.z = DISTANCE_TO_CAM

		# Normalize and use as direction vectors
		r = p.normalize()

		# Intersect with surface
		rmat = np.matrix([
			[self.surfaceX.x, self.surfaceY.x, -self.r.x],
			[self.surfaceX.y, self.surfaceY.y, -self.r.y],
			[self.surfaceX.z, self.surfaceY.z, -self.r.z]
		])
		o = np.array([[self.start.x], [self.start.y], [self.start.z]])
		r = rmat.I * o
		return Vec2(r[0], r[1])

	def findBounds(self):
		# Get 2D coordinates of edges of the screen
		points = [
			(        0, IMG_HEIGHT),
			(        0,          0),
			(IMG_WIDTH,          0),
			(IMG_WIDTH, IMG_HEIGHT)
		]
		points = map(self.surfaceMapSingle, points)
		bl, tl, tr, br = points

		# Find bounds and adjust
		bl.x = max(bl.x, tl.x)
		tl.x = max(bl.x, tl.x)
		tr.x = min(tr.x, br.x)
		br.x = min(tr.x, br.x)
		tl.y = max(tl.y, tr.y)
		tr.y = max(tl.y, tr.y)
		bl.y = min(bl.y, br.y)
		br.y = min(bl.y, br.y)

		xoffset = self.framex * abs(bl.x - br.x)
		yoffset = self.framey * abs(bl.y - tl.y)
		bloffset = Vec2(xoffset, -yoffset)
		troffset = Vec2(-xoffset, yoffset)

		return bl + bloffset, tr + troffset

	def mapPicture(self, points):
		# Fit picture space into the bounds of the surface
		bl, tr = self.findBounds()
		width, height = abs(bl.x - tr.x), abs(bl.y - tr.y)
		if float(width) / height > float(PIC_WIDTH) / PIC_HEIGHT:
			width = height * (PIC_WIDTH / PIC_HEIGHT)
		else:
			height = width * (PIC_HEIGHT / PIC_WIDTH)
		tr = bl + Vec2(width, -height)

		# Convert pixel points into surface coordinates
		for i in range(len(points)):
			x, y = points[i]
			x, y = bl.x + x * width / PIC_WIDTH, bl.y - (PIC_HEIGHT - y) * height / PIC_HEIGHT
			points[i] = Vec2(x, y)

		return points
