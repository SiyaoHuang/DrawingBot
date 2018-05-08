import pigpio

# Pin assignments
PIN_LEFT_SERVO = 12
PIN_RIGHT_SERVO = 13
PIN_PEN_SERVO = 18

class Servo(object):
	def __init__(self, pi, pin, dir='cw', trim=0):
		self.pin = pin
		self.maxspd = 0.002
		self.minspd = 0.001
		self.period = 0.020
		self.maxduty = 100 * self.maxspd / self.period
		self.minduty = 100 * self.minspd / self.period
		self.dir = 1 if dir == 'cw' else -1
		self.trim = trim
		self.duty = 0
		
		self.pi = pi
		self.pi.set_mode(self.pin, pigpio.OUTPUT)
		self.pi.hardware_PWM(self.pin, 1 / self.period, 0.0)

	def turn(self, i):
		i += self.trim
		i *= self.dir
		i = (i + 1) / 2.0
		duty = 1000000 * (self.minspd + i * (self.maxspd - self.minspd)) / self.period
		self.duty = duty
                self.pi.hardware_PWM(self.pin, 1 / self.period, duty)

	def adjustDuty(self, dx):
		dx *= self.dir
		self.pi.hardware_PWM(self.pin, 1 / self.period, self.duty + dx)
                
	def stop(self):
                self.pi.hardware_PWM(self.pin, 0.0, 0.0)

class Bot(object):
	def __init__(self):
		# initialize servos
		self.pi_hw = pigpio.pi()
		self.leftServo = Servo(self.pi_hw, PIN_LEFT_SERVO, 'cw')
		self.rightServo = Servo(self.pi_hw, PIN_RIGHT_SERVO, 'ccw')
		#self.penServo = Servo(self.pi_hw, PIN_PEN_SERVO, 'cw')
		self.pen = False

	def rotate(self, i):
		self.leftServo.turn(i)
		self.rightServo.turn(-i)

	def forward(self, i):
		self.leftServo.turn(i)
		self.rightServo.turn(i)

	def adjust(self, dx):
		self.leftServo.adjustDuty(dx / 2)
		self.rightServo.adjustDuty(-dx / 2)

	def penDown(self, i):
		self.penServo.turn(i)
		self.pen = True

	def penUp(self, i):
		self.penServo.turn(i)
		self.pen = False

	def stop(self):
		self.leftServo.stop()
		self.rightServo.stop()

