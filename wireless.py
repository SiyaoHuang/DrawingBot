import socket
from bot import *
# Commands
BOT_FORWARD = 0
BOT_ROTATE  = 1
BOT_STOP    = 2
BOT_ADJUST  = 3
BOT_PENUP   = 4
BOT_PENDOWN = 5

class VirtualBotTX(object):
	def __init__(self, ip, port):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind((ip, port))
		self.s.listen(1)
		self.conn, self.addr = s.accept()
		print 'Connected to:', self.addr

	def close(self):
		self.conn.close()

	def makePacket(self, cmd, arg):
		return "%i %f\n" % (cmd, arg)

	def rotate(self, i):
		self.s.send(self.makePacket(BOT_ROTATE, i))

	def forward(self, i):
		self.s.send(self.makePacket(BOT_FORWARD, i))

	def adjust(self, dx):
		self.s.send(self.makePacket(BOT_ADJUST, dx))

	def penDown(self, i):
		self.s.send(self.makePacket(BOT_PENDOWN, i))

	def penUp(self, i):
		self.s.send(self.makePacket(BOT_PENUP, i))

	def stop(self):
		self.s.send(self.makePacket(BOT_STOP, 0))

class VirtualBotRX(object):
	def __init__(self, ip, port):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((ip, port))
		self.buffer = ""
		self.bot = Bot()
		print 'Connected!'

	def getCommand(self):
		self.buffer += self.s.recv(1024)
		if self.buffer != "":
			pos = self.buffer.find('\n')
			line = self.buffer[:pos]
			self.buffer = self.buffer[pos + 1:]

			cmd, arg = line.split()
			print 'command:', int(cmd), float(arg)
			return cmd, arg
		return None

	def execute(self):
		nxt = self.getCommand()
		while nxt == None:
			nxt = self.getCommand()

		cmd, arg = nxt
		if cmd == BOT_FORWARD:
                        print 'executing forward'
			self.bot.forward(arg)
		elif cmd == BOT_ROTATE:
			self.bot.rotate(arg)
		elif cmd == BOT_STOP:
			self.bot.stop()
		elif cmd == BOT_ADJUST:
			self.bot.adjust(arg)
		elif cmd == BOT_PENUP:
			self.bot.penUp(arg)
		elif cmd == BOT_PENDOWN:
			self.bot.penDown(arg)

