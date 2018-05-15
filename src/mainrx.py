from wireless import *
import time

bot = VirtualBotRX()
while True:
	time.sleep(3)
	try:
		bot.connect()
		bot.run()
	except socket.error:
		print 'Trying to connect...'