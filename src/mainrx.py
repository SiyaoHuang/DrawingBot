from wireless import *
import time

while True:
	time.sleep(3)
	try:
		bot = VirtualBotRX()
		bot.run()
	except socket.error:
		print 'Trying to connect...'