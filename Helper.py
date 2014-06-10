import ode
import objects

class MoreMass(objects.ODEThing):
	def __init__(self, helper):
		self.helper = helper
		objects.ODEThing.__init__(self)
	
	def construct(self):
		self.body = ode.Body(objects.world)
		x, y, _ = self.helper.getPosition()
		self.body.setPosition((x, y, 0))
		M = ode.Mass()
		M.setSphereTotal(self.helper.strong_mass, self.helper.rad)
		self.body.setMass(M)
		objects.ODEThing.construct(self)
		self.body.setAngularVel(self.helper.getAngularVel())
		self.body.setLinearVel(self.helper.body.getLinearVel())
		self.fixed_joint = ode.FixedJoint(objects.world, self.jointgroup)
		self.fixed_joint.attach(self.body, self.helper.body)
		self.fixed_joint.setFixed()
	
	def destroy(self):
		self.jointgroup.empty()
		del self.body
		del self.fixed_joint
		
	def setPosition(self, pos):
		x, y = pos
		self.body.setPosition((x,y,0))
	
	def draw(self):
		pass # because no geom

class Helper(objects.Ball):
	def __init__(self, pos):
		self.weak_mass = 0.05
		objects.Ball.__init__(self, pos, 0.1, self.weak_mass)
		self.strong_mass = 1
		self.is_strong = False
		self.dirs = [False, False, False, False] # WASD (up left down right)
	
	# TODO: it seems we can't dynamically change mass.
	# I may be able to create a new body w/ added mass, and use a fixed joint
	# to emulate increased mass.
	def become_stronger(self):
		self.is_strong = True
		self.more = MoreMass(self)
	
	def become_weaker(self):
		self.is_strong = False
		self.more.destruct()
		del self.more
	
	def setPosition(self, pos):
		x, y = pos
		self.body.setPosition((x,y,0))
		if hasattr(self, 'more'):
			self.more.setPosition(pos)
	
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
