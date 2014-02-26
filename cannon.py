import math

import constants
import render
import objects

class Cannon(objects.Thing):
	def __init__(self, pos, direction):
		objects.Thing.__init__(self)
		x, y = pos
		d1, d2 = direction
		d_len = math.sqrt(d1 * d1 + d2 * d2)
		d1 /= d_len; d2 /= d_len;
		self.launch = 1
		self.pos = pos
		self.direction = direction
	def update(self):
		self.launch -= constants.dt
		if (self.launch < 0):
			if hasattr(self, 'ball'): self.ball.destruct(); del self.ball
			self.launch = 10
			#self.ball = objects.Ball(self.pos, 0.1)
			self.ball = objects.Box(self.pos, (0.1, 0.1))
			x, y = self.direction
			self.ball.addForce((1000*x,1000*y))
	def draw(self):
		render.drawPoint(self.pos)
