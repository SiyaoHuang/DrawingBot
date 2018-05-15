from wireless import *
import time

while True:
	time.sleep(3)
	try:
		bot = VirtualBotRX()
	except socket.error:
		continue

	bot.run()