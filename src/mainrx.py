# mainrx.py
#
# Main module that runs on the bot that continually
# tries to connect. Once connected, it executes 
# any received commands.

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