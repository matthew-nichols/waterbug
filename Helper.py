import ode
import objects

class Helper(objects.Ball):
	def __init__(self, pos):
		self.weak_mass = 0.05
		objects.Ball.__init__(self, pos, 0.1, self.weak_mass)
		self.strong_mass = 0.1
		self.is_strong = False
		self.dirs = [False, False, False, False] # WASD (up left down right)
	
	# TODO: it seems we can't dynamically change mass.
	# I may be able to create a new body w/ added mass, and use a fixed joint
	# to emulate increased mass.
	def become_stronger(self):
		self.is_strong = True
	
	def become_weaker(self):
		self.is_strong = False
	
	def update(self):
		if self.is_strong:
			strength = 2
			if self.dirs[0]:
				self.addForce((0,-strength))
			if self.dirs[1]:
				self.addForce((-strength,0))
			if self.dirs[2]:
				self.addForce((0,strength))
			if self.dirs[3]:
				self.addForce((strength,0))
		else:
			strength = 0.1
			if self.dirs[0]:
				self.addForce((0,-strength))
			if self.dirs[1]:
				self.addForce((-strength,0))
			if self.dirs[2]:
				self.addForce((0,strength))
			if self.dirs[3]:
				self.addForce((strength,0))
			
		objects.Ball.update(self)
