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
	obj_list += create_list
	create_list = []

class Thing:
	def __init__(self):
		create_list.append(self)
	def draw(self):
		pass	
	def update(self):
		pass
	def destruct(self):
		destroy_list.append(self)

class ODEThing(Thing):
	""" handles the plane joint and such common among objects"""
	def __init__(self):
		Thing.__init__(self)
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
	def destroy(self):
		self.geom.getSpace().remove(self.geom)
		del self.geom; del self.joint; del self.body
	
	def addForce(self, force):
		x, y = force
		self.body.addForce((x,y,0))
	
	def addTorque(self, torque):
		self.body.addTorque((0,0,torque))
	
	def setRotation(radians):
		self.body.setRotation((math.cos(radians), math.sin(radians), 0, -math.sin(radians), math.cos(radians), 0, 0, 0, 1))
		
class Box(ODEThing):
	def __init__(self, pos=(0,0), lengths=(1,1), mass=1):
		x, y = pos; L, H = lengths
		self.body = ode.Body(world)
		M = ode.Mass()
		M.setBoxTotal(mass, L, H, 1)
		self.body.setMass(M)
		self.body.setPosition((x,y,0))		
		self.geom = ode.GeomBox(space, (L,H,1))
		self.geom.setBody(self.body)
		ODEThing.__init__(self)

class Ball(ODEThing):
	def __init__(self, pos=(0,0), rad=1, mass=1):
		x,y = pos
		self.body = ode.Body(world)
		M = ode.Mass()
		M.setSphereTotal(mass, rad)
		self.body.setMass(M)
		self.body.setPosition((x,y,0))
		self.geom = ode.GeomSphere(space, rad)
		self.geom.setBody(self.body)
		ODEThing.__init__(self)

class Capsule(ODEThing):
	""" makes a capsule, pointing into x by default """
	def __init__(self, pos=(0,0), radius=1, length=1, mass=1):
		self.radius = radius
		self.length = length
		x, y = pos
		self.body = ode.Body(world)
		M = ode.Mass()
		M.setCappedCylinderTotal(mass, 1, radius, length)
		self.body.setMass(M)
		self.body.setPosition((x,y,0))
		self.geom = ode.GeomTransform(space)
		self.geom2 = ode.GeomCapsule(None, radius, length)
		self.geom2.setRotation((0,0,1,1,0,0,0,1,0)) # make z point into x
		self.geom.setBody(self.body)
		self.geom.setGeom(self.geom2)
		ODEThing.__init__(self)
	
	def draw(self):
		x, y, _ = self.body.getPosition()
		rot = self.body.getRotation()
		render.drawCapsule((x,y), self.length, 2*self.radius, rot[0], rot[1])
		
