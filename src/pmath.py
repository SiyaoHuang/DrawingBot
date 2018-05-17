# pmath.py
#
# Provides vector math functions for perspective mapping

class Vec3(object):
	def __init__(self, x, y, z):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)

	def clone(self):
		return Vec3(self.x, self.y, self.z)

	def cross(self, other):
		ax, ay, az = self.x, self.y, self.z
		bx, by, bz = other.x, other.y, other.z
		return Vec3(ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bx)

	def mag(self):
		return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** .5

	def normalize(self):
		m = self.mag()
		self.x /= m
		self.y /= m
		self.z /= m
		return self

	def dist_to(self, other):
		return (self - other).mag()

	def vals(self):
		return (self.x, self.y, self.z)

	def __mul__(self, other):
		if type(other) == Vec3:
			return self.x * other.x + self.y * other.y + self.z * other.z
		return Vec3(self.x * other, self.y * other, self.z * other)

	def __div__(self, other):
		return Vec3(self.x / other, self.y / other, self.z / other)

	def __add__(self, other):
		assert type(other) == Vec3
		return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		assert type(other) == Vec3
		return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

	def __rsub__(self, other):
		assert type(other) == Vec3
		return Vec3(other.x - self.x, other.y - self.y, other.z - self.z)

	__rmul__ = __mul__
	__radd__ = __add__

	def __str__(self):
		return "<%f, %f, %f>" % (self.x, self.y, self.z)

class Vec2(object):
	def __init__(self, x, y):
		self.x = float(x)
		self.y = float(y)

	def clone(self):
		return Vec2(self.x, self.y)

	def cross(self, other):
		return self.x * other.y - other.x * self.y

	def mag(self):
		return (self.x ** 2 + self.y ** 2) ** .5

	def normalize(self):
		m = self.mag()
		self.x /= m
		self.y /= m
		return self

	def dist_to(self, other):
		return (self - other).mag()

	def vals(self):
		return (self.x, self.y)

	def __mul__(self, other):
		if type(other) == Vec2:
			return self.x * other.x + self.y * other.y
		return Vec2(self.x * other, self.y * other)

	def __div__(self, other):
		return Vec2(self.x / other, self.y / other)

	def __add__(self, other):
		assert type(other) == Vec2
		return Vec2(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		assert type(other) == Vec2
		return Vec2(self.x - other.x, self.y - other.y)

	def __rsub__(self, other):
		assert type(other) == Vec2
		return Vec2(other.x - self.x, other.y - self.y)

	__rmul__ = __mul__
	__radd__ = __add__

	def __str__(self):
		return "<%f, %f>" % (self.x, self.y)

class PFunction(object):
	def __init__(self, f, eps):
		self.f = f
		self.eps = eps

	def __call__(self, x):
		return self.f(x)

	# Finds the slope of the function at a certain point.
	def slope(self, x):
		prev = self.f(x)
		nxt = self.f(x - self.eps)
		if None in [prev, nxt]:
			return None
		return (self.f(x) - self.f(x - self.eps)) / self.eps

	# Finds the end of the function in a certain range and return 
	# the input value.
	def findEnd(self, a, b):
		left, right = a, b
		while right - left > self.eps:
			middle = (left + right) / 2
			if self.f(middle) == None:
				right = middle
			else:
				left = middle
		return left

	# Finds the minimum of a function given a domain interval and
	# returns the input value for which the function is minimum. Works
	# only for unimodal functions.
	def findMin(self, a, b):
		left, right = a, b
		while right - left > self.eps:
			middle = (left + right) / 2
			smiddle = self.slope(middle)
			if smiddle == None:
				return None
			if smiddle > 0:
				right = middle
			else:
				left = middle
		return (left + right) / 2