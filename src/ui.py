import sys, time, pygame
import math
import os
import RPi.GPIO as GPIO
from controller import *

##os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
##os.putenv('SDL_FBDEV', '/dev/fb1')
##os.putenv('SDL_MOUSEDRV', 'TSLIB')    #Track mouse clicks
##os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

# timer
start_time = time.time()

# Initialize GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pygame.init()
pygame.mouse.set_visible(True)

size = width, height = 320, 240
black = 0, 0, 0
white = 255, 255, 255

screen = pygame.display.set_mode(size)

##my_font = pygame.font.Font(None, 50)
##WHITE = 255, 255, 255
##my_text, text_pos = 'quit', (80,180)
##text_surface = my_font.render(my_text, True, WHITE)
##rect = text_surface.get_rect(center=text_pos)
##
##text_coords = ""
##text_surface_coords = my_font.render(text_coords, True, WHITE)
##text_coords_rect = text_surface_coords.get_rect(center=(160, 120))
points = []
start = time.time()
c = Controller()
while time.time() - start < 10:
    if not GPIO.input(22):
        sys.exit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            x, y = pygame.mouse.get_pos()
            dist = 20
            for i in points:
                xi, yi = i
                if ((xi - x)**2 + (yi - y)**2)**.5 < dist:
                    x, y = xi, yi
                    break
            points += [(x, y)]
            print x, y
    
    screen.fill(white)
    for i in points:
        pygame.draw.circle(screen, black, i, 2)
    if len(points) > 1:
        pygame.draw.lines(screen, black, False, points, 2)
    pygame.display.flip()

    time.sleep(0.01)

c.drawPoints()

GPIO.cleanup()
sys.exit()

