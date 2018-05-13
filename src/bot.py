import pigpio
import RPi.GPIO as GPIO
import time

# Pin assignments
PIN_LEFT_SERVO  = 12
PIN_RIGHT_SERVO = 13
PIN_PEN_SERVO   = 21

class Servo(object):
	def __init__(self, pi, pin, dir='cw', trim=0, hw=True):
		self.pin = pin
		self.maxspd = 0.002
		self.minspd = 0.001
		self.period = 0.020
		self.dir = 1 if dir == 'cw' else -1
		self.trim = trim
		self.duty = 0
		self.hw = hw
		if not hw:
			GPIO.setup(self.pin, GPIO.OUT)
			self.pwm = GPIO.PWM(self.pin, 1 / self.period)
			self.pwm.start(0)
			return

		self.pi = pi
		self.pi.set_mode(self.pin, pigpio.OUTPUT)
		self.pi.hardware_PWM(self.pin, 1 / self.period, 0.0)

	def turn(self, i):
		i += self.trim
		i *= self.dir
		i = (i + 1) / 2.0
		duty = 1000000 * (self.minspd + i * (self.maxspd - self.minspd)) / self.period
		duty = min(max(0, duty), 1000000)
		self.duty = duty

		if not self.hw:
			self.pwm.ChangeDutyCycle(0.0001 * self.duty)
			return
		self.pi.hardware_PWM(self.pin, 1 / self.period, duty)

	def adjustDuty(self, dx):
		if not self.hw:
			return
		dx *= self.dir
		duty = min(max(0, self.duty + dx), 1000000)
		self.pi.hardware_PWM(self.pin, 1 / self.period, duty)

	def stop(self):
		if not self.hw:
			self.pwm.ChangeDutyCycle(0)
			return
		self.pi.hardware_PWM(self.pin, 0.0, 0.0)

class Bot(object):
	def __init__(self):
		# initialize servos
		GPIO.setmode(GPIO.BCM)
		pi_hw = pigpio.pi()
		self.leftServo = Servo(pi_hw, PIN_LEFT_SERVO, 'cw')
		self.rightServo = Servo(pi_hw, PIN_RIGHT_SERVO, 'ccw')
		self.penServo = Servo(pi_hw, PIN_PEN_SERVO, 'cw', hw=False)
		self.pdsleep = 0.0
		self.pusleep = 0.0

	def rotate(self, i):
		self.leftServo.turn(i)
		self.rightServo.turn(-i)

	def rotateAdjust(self, i):
		self.rotate(i)
		time.sleep(0.01)
		self.stop()

	def forward(self, i):
		self.leftServo.turn(i)
		self.rightServo.turn(i)

	def forwardAdjust(self, i):
		self.forward(i)
		time.sleep(0.01)
		self.stop()

	def adjust(self, dx):
		self.leftServo.adjustDuty(dx / 2)
		self.rightServo.adjustDuty(-dx / 2)

	def penDown(self, i):
		self.penServo.turn(i)
		time.sleep(self.pdsleep)
		self.penServo.stop()

	def penUp(self, i):
		self.penServo.turn(i)
		time.sleep(self.pusleep)
		self.penServo.stop()

	def penDownSLeep(self, i):
		self.pdsleep = i

	def penUpSleep(self, i):
		self.pusleep = i

	def trimLeft(self, i):
		self.leftServo.trim = i

	def trimRight(self, i):
		self.rightServo.trim = i

	def stop(self):
		self.leftServo.stop()
		self.rightServo.stop()
