from wireless import *
import time

# Read in points as array
##pointArray = []
##
### Create controller and set it up
##controller = Controller()
##controller.calibrate()
##controller.gotoTarget(Vec2(0.0, 0.0))
bot = VirtualBotRX('10.148.5.69', 5006)
while True:
    bot.execute()

##GPIO.setmode(GPIO.BCM)
##pi_hw = pigpio.pi()
##s = Servo(pi_hw, 13, 'cw')
##s.turn(0.0)
##print s.duty
##while True:
##    pass
##


####for i in pointArray:
####	print "drawing point " + str(i)
####	controller.gotoTarget(i)
##
##print "done."

