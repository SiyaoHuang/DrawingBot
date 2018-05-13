from controller import *
import time
import sys

c = Controller()
print "calibrating..."
c.calibrate()
print "finished", str(c.pmap.surfaceNormal)
points = [
    (0.7, 0),
    (2, -4),
    (3.3, 0),
    (0, -2.3),
    (4, -2.3),
    (0.7, 0)
]

c.gotoTarget(Vec2(0, 0))
for i in range(len(points)):
    if i == 0:
        c.bot.penDown(c.dnspeed)
        time.sleep(2)
        c.bot.penUp(c.upspeed)
        time.sleep(2)
    v = Vec2(points[i][0], points[i][1])
    c.gotoTarget(v, draw=i != 0)
c.gotoTarget(Vec2(0, 0))

##c.gotoTarget(Vec2(0.0, 0.0))
##while True:
##    c.gotoTarget(Vec2(4.0,  0.0), draw=True)
##    print "--------------got to 4,  0"
##    c.gotoTarget(Vec2(4.0, -4.0), draw=True)
##    print "--------------got to 4, -4"
##    c.gotoTarget(Vec2(0.0, -4.0), draw=True)
##    print "--------------got to 0, -4"
##    c.gotoTarget(Vec2(0.0,  0.0), draw=True)
##    print "--------------got to 0,  0"

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

