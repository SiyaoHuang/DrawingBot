import RPi.GPIO as GPIO

# Pin assignments
PIN_LEFT_SERVO = 3
PIN_RIGHT_SERVO = 5
PIN_PEN_SERVO = 7

class Servo(object):
	def __init__(self, pin, dir='cw'):
		self.pin = pin
		self.maxspd = 0.002
		self.minspd = 0.001
		self.period = 0.020
		self.maxduty = self.maxspd / self.period
		self.minduty = self.minspd / self.period
		self.dir = 1 if 'cw' else -1

		GPIO.setup(self.pin, GPIO.OUT)
		self.pwm = GPIO.PWM(self.pin, 1 / self.period)
		self.duty = 0

	def turn(self, i):
		i *= self.dir
		i = (i + 1) / 2.0
		duty = 100 * (self.minspd + i * (self.maxspd - self.minspd)) / self.period
		self.duty = duty
		self.pwm.start(duty)

	def adjustDuty(self, dx):
		dx *= self.dir
		self.duty += dx
		self.duty = min(max(self.minduty, self.duty), self.maxduty)
		self.pwm.ChangeDutyCycle(self.duty)

	def stop(self):
		self.pwm.stop()

class Bot(object):
	def __init__(self):
		# initialize servos
		GPIO.setmode(GPIO.BOARD)
		self.leftServo = Servo(PIN_LEFT_SERVO, 'cw')
		self.rightServo = Servo(PIN_RIGHT_SERVO, 'ccw')
		self.penServo = Servo(PIN_PEN_SERVO, 'cw')
		self.pen = False

	def rotate(self, i):
		self.leftServo.turn(i)
		self.rightServo.turn(i)

	def forward(self, i):
		self.leftServo.turn(i)
		self.rightServo.turn(i)

	def adjust(self, dx):
		self.leftServo.adjustDuty(dx / 2)
		self.rightServo.adjustDuty(-dx / 2)

	def penDown(self):
		self.penServo.turn(i)
		self.pen = True

	def penUp(self):
		self.penServo.turn(i)
		self.pen = False

	def stop(self):
		self.leftServo.stop()
		self.rightServo.stop()

