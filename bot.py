import RPi.GPIO as GPIO

# Pin assignments
PIN_LEFT_SERVO = 0
PIN_RIGHT_SERVO = 0
PIN_PEN_SERVO = 0

class Servo(object):
	def __init__(self, pin):
		self.pin = pin
		self.maxspd = 0.002
		self.minspd = 0.001
		self.period = 0.020

		GPIO.setup(self.pin, GPIO.OUT)
		self.pwm = GPIO.PWM(self.pin, 1 / self.period)

	def turn(self, i):
		i = (i + 1) / 2.0
		duty = 100 * (self.minspd + i * (self.maxspd - self.minspd)) / self.period
		self.pwm.start(duty)

	def stop(self):
		self.pwm.stop()

class Bot(object):
	def __init__(self):
		# initialize servos
		GPIO.setmode(GPIO.BOARD)
		self.leftServo = Servo(PIN_LEFT_SERVO)
		self.rightServo = Servo(PIN_RIGHT_SERVO)
		self.penServo = Servo(PIN_PEN_SERVO)
		self.pen = False

	def rotate(self, i):
		self.leftServo.turn(i)
		self.rightServo.turn(i)

	def forward(self, i):
		self.leftServo.turn(i)
		self.rightServo.turn(-i)

	def penDown(self):
		self.penServo.turn(i)
		self.pen = True

	def penUp(self):
		self.penServo.turn(-i)
		self.pen = False

	def stop(self):
		self.leftServo.stop()
		self.rightServo.stop()

