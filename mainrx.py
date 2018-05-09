from wireless import *
import controller

bot = VirtualBotRX(controller.IP_ADDR, controller.PORT)
while True:
    bot.execute()