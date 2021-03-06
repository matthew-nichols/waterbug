import ode

import constants
import objects
import render
import weakref
import random

class XFactor(objects.Thing):
	for_player = True
	def __init__(self, player):
		objects.Thing.__init__(self)
		self.timeout = 5.0 # seconds
	def update(self):
		self.timeout -= constants.dt
		for i in objects.obj_list:
			if hasattr(i, 'addForce'):
				i.addForce((5,0))
		if self.timeout <= 0:
			self.destruct()

class Strength(objects.Thing):
	for_helper = True
	def __init__(self, helper):
		objects.Thing.__init__(self)
		self.timeout = 15.0
		self.helper = helper
		helper.become_stronger()
	def update(self):
		self.timeout -= constants.dt
		if self.timeout <= 0:
			self.helper.become_weaker()
			self.destruct()	
	
	def destroy(self):
		x, y = random.randint(0, 3), random.randint(0, 3)
		Pickup((x + 0.5, y + 0.5), 5, Strength)	

class Pickup(objects.Thing):
	def __init__(self, pos, offset, pickup, radius = 0.1):
		self.pos = pos
		self.offset = offset
		self.radius = 0.05
		self.pickup = pickup
		self.color = render.blue
		objects.Thing.__init__(self)
	
	def construct(self):
		self.geom1 = ode.GeomSphere(objects.space, self.radius)
		self.geom2 = ode.GeomSphere(objects.space, self.radius)
		self.geom1.setPosition((self.pos[0], self.pos[1], 0))
		self.geom2.setPosition((self.pos[0] + self.offset, self.pos[1], 0))
		self.geom1.data = weakref.ref(self)
		self.geom2.data = weakref.ref(self)
	
	def destroy(self):
		self.geom1.getSpace().remove(self.geom1)
		self.geom2.getSpace().remove(self.geom2)
		del self.geom1; del self.geom2
	
	def draw(self):
		render.drawCircle(self.pos, self.radius, self.color)
		render.drawCircle((self.pos[0] + self.offset, self.pos[1]), self.radius, self.color)
	
	def onCollision(self, other):
		if getattr(self.pickup, 'for_helper', False) and getattr(other, 'tag', '') == 'helper':
			self.pickup(other)
			self.destruct()
		elif getattr(self.pickup, 'for_player', False) and getattr(other, 'tag', '') == 'player':
			self.pickup(other)
			self.destruct()
		return False
