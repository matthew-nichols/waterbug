import ode
import pygame
import math
import weakref

import render

world = ode.World()
world.setERP(0.8)
world.setCFM(1e-5)

contactgroup = ode.JointGroup()
space = ode.HashSpace()

obj_list = []

create_list = []
destroy_list = []

def update_obj_list():
	global obj_list, destroy_list, create_list
	# really inefficient...
	for i in destroy_list:
		i.destroy()
		obj_list.remove(i)
	destroy_list = []
	for i in create_list:
		i.construct()
		obj_list.append(i)
	create_list = []

def construct_now(obj):
	obj.construct()
	create_list.remove(obj)
	obj_list.append(obj)

class Thing:
	def __init__(self):
		"""initializes the object. DO NOT ADD GEOMS/BODIES TO SPACES HERE!"""
		create_list.append(self)
	def construct(self):
		"""construct ODE-specific stuff (that needs to be done after the collision callback"""
		pass
	def destruct(self):
		"""schedules for destruction, should not be overridden. """
		destroy_list.append(self)
	def destroy(self):
		"""destroy ODE stuff here. """
		pass
	def draw(self):
		""" custom draw logic"""
		pass	
	def update(self):
		""" custom update logic"""
		pass
	
	def onCollision(self,other):
		""" returns True if physics should proceed, otherwise return False """
		return True

class DebugPoint(Thing):
	def __init__(self, pos=(0,0), frames = 5):
		self.pos = pos
		self.frames = frames
		Thing.__init__(self)
	
	def draw(self):
		render.drawPoint(self.pos)
	
	def update(self):
		self.frames -= 1
		if self.frames <= 0:
			self.destruct()

class ODEThing(Thing):
	""" handles the plane joint and such common among objects"""
	def construct(self):
		self.joint = ode.Plane2DJoint(world)
		self.joint.attach(self.body, ode.environment)
		self.body.data = weakref.ref(self)
	def draw(self):
		render.drawGeom(self.geom)
	def update(self):
		r, _, _, z = self.body.getQuaternion()
		quat_len = math.sqrt(r * r + z * z)
		r /= quat_len; z /= quat_len;
		self.body.setQuaternion((r,0,0,z))
		_, _, v = self.body.getAngularVel()
		self.body.setAngularVel((0,0,v))
		x, y, z = self.body.getPosition()
		#if (abs(z) > 0.01): print "what?"
	def destroy(self):
		self.geom.getSpace().remove(self.geom)
		del self.geom; del self.joint; del self.body
	
	def addForce(self, force):
		x, y = force
		self.body.addForce((x,y,0))
	
	def addTorque(self, torque):
		if type(torque) in [float,int]:
			self.body.addTorque((0,0,torque))
		else:
			self.body.addTorque((0,0,torque[1]))
	
	def setRotation(self, radians):
		self.body.setRotation((math.cos(radians), math.sin(radians), 0, -math.sin(radians), math.cos(radians), 0, 0, 0, 1))
	
	def getMass(self):
		self.body.getMass()
	
	def getAngularVel(self):
		# TODO: return 2d angular velocity, Ragdoll.py needs 3D for now
		return self.body.getAngularVel()
	
	def setAngularVel(self, pos):
		# TODO: same
		x, _, y = pos
		self.body.setAngularVel((x, y, 0))
	
	def getPosition(self):
		# TODO: same
		return self.body.getPosition()
		
class Box(ODEThing):
	def __init__(self, pos=(0,0), lengths=(1,1), mass=1):
		self.x, self.y = pos
		self.L, self.H = lengths
		self.mass = mass
		ODEThing.__init__(self)
		
	def construct(self):
		self.body = ode.Body(world)
		M = ode.Mass()
		M.setBoxTotal(self.mass, self.L, self.H, 1)
		self.body.setMass(M)
		self.body.setPosition((self.x,self.y,0))		
		self.geom = ode.GeomBox(space, (self.L,self.H,10))
		self.geom.setBody(self.body)
		ODEThing.construct(self)

class Ball(ODEThing):
	def __init__(self, pos=(0,0), rad=1, mass=1):
		self.x, self.y = pos; self.rad = rad; self.mass = mass
		ODEThing.__init__(self)
	def construct(self):
		self.body = ode.Body(world)
		M = ode.Mass()
		M.setSphereTotal(self.mass, self.rad)
		self.body.setMass(M)
		self.body.setPosition((self.x,self.y,0))
		self.geom = ode.GeomSphere(space, self.rad)
		self.geom.setBody(self.body)
		ODEThing.construct(self)

class Capsule(ODEThing):
	""" makes a capsule, pointing into x by default """
	def __init__(self, pos=(0,0), radius=1, length=1, mass=1, start_angle=0):
		self.radius = radius
		self.length = length
		self.x, self.y = pos; self.mass = mass; self.start_angle = start_angle
		ODEThing.__init__(self)
		
	def construct(self):
		self.body = ode.Body(world)
		M = ode.Mass()
		M.setCappedCylinderTotal(self.mass, 1, self.radius, self.length)
		self.body.setMass(M)
		self.body.setPosition((self.x,self.y,0))
		self.setRotation(self.start_angle)
		self.geom = ode.GeomTransform(space)
		self.geom2 = ode.GeomCapsule(None, self.radius, self.length) # by default points into z
		self.geom2.setRotation((0,0,1,1,0,0,0,1,0)) # make z point into x
		self.geom.setBody(self.body)
		self.geom.setGeom(self.geom2)
		ODEThing.construct(self)
	
	def draw(self):
		x, y, _ = self.body.getPosition()
		rot = self.body.getRotation()
		render.drawCapsule((x,y), self.length, 2*self.radius, rot[0], rot[1])
		
