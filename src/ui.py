import sys, time, pygame
import math
import os
import RPi.GPIO as GPIO
from controller import *

os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')    # Track mouse clicks
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

# timer
start_time = time.time()

# Initialize GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pygame.init()
pygame.mouse.set_visible(True)

size = width, height = 320, 240
black = 0, 0, 0
white = 255, 255, 255

screen = pygame.display.set_mode(size)
my_font = pygame.font.Font(None, 25)

distance = 62

sqr_surface = my_font.render("Clear", True, black)
sqr_pos = sqr_x, left_y = 280, 40
sqr_rect = sqr_surface.get_rect(center=sqr_pos)

done_surface = my_font.render("Done", True, black)
done_pos = done_x, done_y = 290, 40 + distance
done_rect = done_surface.get_rect(center=done_pos)

undo_surface = my_font.render("Undo", True, black)
undo_pos = undo_x, undo_y = 290, 40 + 2*distance
undo_rect = undo_surface.get_rect(center=undo_pos)

redo_surface = my_font.render("Redo", True, black)
redo_pos = redo_x, redo_y = 290, 40 + 3*distance
redo_rect = redo_surface.get_rect(center=redo_pos)

show_buttons = True 
points = []
pointsredo = []
start = time.time()
c = Controller()
timer = 0
while True:
	if not GPIO.input(17):
		#points = [ (30,30) , (30, 210), (210,210), (210,30),(30,30)]
		#pointsredo = []
		points = []
		pointsredo = []
		time.sleep(0.2)
	if not GPIO.input(22):
		break
	if not GPIO.input(23):
		if points != []:
			pointsredo = [points[0]] + pointsredo
			del points[0]
		time.sleep(0.2)
	if not GPIO.input(27):
		if pointsredo != []:
			points = [pointsredo[0]] + points
			del pointsredo[0]
		time.sleep(0.2)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.MOUSEBUTTONUP:
			show_buttons = False
			timer = 100
			x, y = pygame.mouse.get_pos()
			dist = 20
			for i in points:
				xi, yi = i
				if ((xi - x)**2 + (yi - y)**2)**.5 < dist:
					x, y = xi, yi
					break
			points = [(x, y)] + points
			pointsredo = []
			print x, y
	
	if not show_buttons:
		if timer == 0:
			show_buttons = True
		timer -= 1

	screen.fill(white)
	for i in points:
		pygame.draw.circle(screen, black, i, 2)
	if len(points) > 1:
		pygame.draw.lines(screen, black, False, points, 2)
		
	if show_buttons:
		screen.blit(sqr_surface, sqr_rect)
		screen.blit(done_surface, done_rect)
		screen.blit(undo_surface, undo_rect)
		screen.blit(redo_surface, redo_rect)
	pygame.display.flip()

	time.sleep(0.01)

c.drawPoints(points[::-1])

GPIO.cleanup()
sys.exit()
