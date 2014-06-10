#!/usr/bin/env python2.7

import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.event as event
import pygame.gfxdraw as gfxdraw
import pygame.time
import pygame.font as font
from pygame import Color
import ode
import math
import objgraph
import datetime
import weakref

import render
import maze
import objects
import constants
import cannon
import Ragdoll
import Water
import charThree
import charBox
import charTriangle
import charTwo
import Pickup
import Helper

the_maze = maze.Maze(4,4)
the_maze.generate_simple2()
maze_space = ode.HashSpace(objects.space)
maze_space.isImmovable = True
the_maze.make_geoms(maze_space)
the_maze.make_geoms(maze_space, 0.1, (5,0))

door_space = ode.HashSpace(objects.space)
door_space.isImmovable = True
doors = the_maze.make_doors(door_space, 0.1, (5,0))

class wind_force(objects.Thing):
	def __init__(self):
		self.time = 0
		objects.Thing.__init__(self)
		
	def update(self):
		self.time += constants.dt
		for g in objects.obj_list:
			if hasattr(g, 'addForce'):
				g.addForce((0, 0.1 * math.sin(0.15 * self.time)))
	
	def draw(self):
		mag = math.sin(0.15 * self.time)
		x, y = 4.5, 2.0
		render.drawLine((x,y), (x,y + 2 * mag), render.red)
				
class destroy_doors(objects.Thing):
	def __init__(self, _):
		objects.Thing.__init__(self)
	
	def update(self):
		self.destruct()
	
	def destroy(self):
		global door_space
		if door_space: objects.space.remove(door_space)
		door_space = 0
		wind_force()
		
	for_player = True

key = Pickup.Pickup((2.5, 2.5), 5, destroy_doors)
key.color = render.red

ball_width = 0.05

def near_callback(args, g1, g2):
	try:
		if getattr(g1, 'isImmovable', False) and getattr(g2, 'isImmovable', False):
			return
		if g1.isSpace() or g2.isSpace():
			if g1.isSpace() and not getattr(g1, 'isImmovable', False):
				g1.collide(args, near_callback)
			if g2.isSpace() and not getattr(g2, 'isImmovable', False):
				g2.collide(args, near_callback)
			ode.collide2(g1, g2, args, near_callback)
		contacts = ode.collide(g1, g2)
	
		if ode.areConnected(g1.getBody(), g2.getBody()):
			return
	
		d1 = getattr(g1.getBody(), 'data', None)
		d2 = getattr(g2.getBody(), 'data', None)
		
		if d1 is None: d1 = getattr(g1, 'data', None)
		if d2 is None: d2 = getattr(g2, 'data', None)
	
		if d1 is not None: d1 = d1()
		if d2 is not None: d2 = d2()
		# TODO: if d1 and/or d2 are not None, use them to handle collision
	
		r1 = True; r2 = True
		
		if len(contacts) > 0:
			if d1 is not None and hasattr(d1, 'onCollision'):
				r1 = d1.onCollision(d2)
			if d2 is not None and hasattr(d2, 'onCollision'):
				r2 = d2.onCollision(d1)

			if r1 and r2:
				for c in contacts:
					c.setBounce(0.8)
					c.setMu(250)
					c.setMode(ode.ContactApprox1)
					objects.DebugPoint(c.getContactGeomParams()[0])
					j = ode.ContactJoint(objects.world, objects.contactgroup, c)
					j.attach(g1.getBody(), g2.getBody())
	except BaseException, e:
		print "Exception in collision handler: ", str(e)

sim_time = pygame.time.get_ticks() / 1000.0

#objects.Capsule((1.7,1.7),0.04,0.4)
ragdoll = Ragdoll.RagDoll(objects.world, objects.space, 1, 0.3, (0.3, 0.5))
objects.construct_now(ragdoll)
ragdoll.addTorque(10)
ragdoll2 = Ragdoll.RagDoll(objects.world, objects.space, 1, 0.3, (0.3+5, 0.5))
objects.construct_now(ragdoll2)
ragdoll2.addTorque(10)

if not constants.jetpack_mode:
	strength = Pickup.Pickup((3.5, 2.5), 5, Pickup.Strength)

ragdoll.tag = 'player'
ragdoll.player_num = 'Left Player'
ragdoll2.tag = 'player'
ragdoll2.player_num = 'Right Player'

monospace = font.SysFont("monospace", 60)

class Victory(objects.Thing):
	def __init__(self, msg):
		objects.Thing.__init__(self)
		self.msg = msg
	
	def construct(self):
		self.texture = monospace.render(self.msg + " wins!", False, render.red)
		self.pos = (640 - self.texture.get_width() / 2, 320 - self.texture.get_height() / 2)
	
	def draw(self):
		render.screen.blit(self.texture, self.pos)
		
class MoveObject(objects.Thing):
	def __init__(self, obj, pos):
		objects.Thing.__init__(self)
		self.obj = obj
		self.pos = pos
	
	def construct(self):
		self.obj.setPosition(self.pos)
		self.destruct()

class VictoryDetection(objects.Thing):
	def __init__(self):
		objects.Thing.__init__(self)
		self.done = False
	
	def construct(self):
		self.geom = ode.GeomBox(objects.space, (20, 1, 1))
		self.geom.setPosition((4.5, 4.7, 0))
		self.geom.data = weakref.ref(self)
	
	def onCollision(self, other):
		if getattr(other, 'tag', '') == 'player' and not self.done:
			Victory(other.player_num)
			self.done = True
			return False
		if getattr(other, 'tag', '') == 'helper':
			return True

VictoryDetection()

class Jetpack(objects.Thing):
	def __init__(self, obj):
		self.obj = obj
		objects.Thing.__init__(self)
		self.dirs = [False, False, False, False]
	
	def update(self):
		strength = 10.0
		if self.dirs[0]:
			self.obj.addForce((0,-strength))
		if self.dirs[1]:
			self.obj.addForce((-strength,0))
		if self.dirs[2]:
			self.obj.addForce((0,strength))
		if self.dirs[3]:
			self.obj.addForce((strength,0))

if not constants.jetpack_mode:
	helper1 = Helper.Helper((0.5, 2.5))
	helper2 = Helper.Helper((5.5, 2.5))
	helper1.tag = 'helper'
	helper2.tag = 'helper'
	helper1.init_pos = ((0.5, 0.5))
	helper2.init_pos = ((5.5, 0.5))
else:
	helper1 = Jetpack(ragdoll)
	helper2 = Jetpack(ragdoll2)

running = True
while running:
	while True:
		e = event.poll()
		if e.type == pygame.NOEVENT:
			break
		elif e.type == pygame.QUIT:
			running = False; break
		elif e.type == pygame.KEYDOWN:
			if e.key == pygame.K_ESCAPE:
				running = False; break
			elif e.key == pygame.K_w:
				helper1.dirs[0] = True
			elif e.key == pygame.K_a:
				helper1.dirs[1] = True
			elif e.key == pygame.K_s:
				helper1.dirs[2] = True
			elif e.key == pygame.K_d:
				helper1.dirs[3] = True
			elif e.key == pygame.K_q:
				ragdoll.setWantedPosition(not ragdoll.wantedPos)
			elif e.key == pygame.K_i:
				helper2.dirs[0] = True
			elif e.key == pygame.K_j:
				helper2.dirs[1] = True
			elif e.key == pygame.K_k:
				helper2.dirs[2] = True
			elif e.key == pygame.K_l:
				helper2.dirs[3] = True
			elif e.key == pygame.K_u:
				ragdoll2.setWantedPosition(not ragdoll2.wantedPos)
			elif e.key == pygame.K_F1:
				render.invert_colors = not render.invert_colors
			elif e.key == pygame.K_F2:
				pygame.image.save(render.screen, datetime.datetime.now().strftime("screenshot-%Y-%m-%d-%H-%M-%S.png"))
		elif e.type == pygame.KEYUP:
			if e.key == pygame.K_w:
				helper1.dirs[0] = False
			elif e.key == pygame.K_a:
				helper1.dirs[1] = False
			elif e.key == pygame.K_s:
				helper1.dirs[2] = False
			elif e.key == pygame.K_d:
				helper1.dirs[3] = False
			elif e.key == pygame.K_i:
				helper2.dirs[0] = False
			elif e.key == pygame.K_j:
				helper2.dirs[1] = False
			elif e.key == pygame.K_k:
				helper2.dirs[2] = False
			elif e.key == pygame.K_l:
				helper2.dirs[3] = False
			
	# FIXME: for some reason, this causes lag when mouse is moving
	#if e.type == pygame.MOUSEMOTION:
	#	water.a1[e.pos[1]/water.size][e.pos[0]/water.size] = 255;
			
	render.screen.fill(render.actual_color((0,0,0)))
	objects.update_obj_list()
	for i in objects.obj_list:
		i.draw()
	if door_space <> 0:
		render.drawGeom(door_space)
	display.flip()
	
	now_time = pygame.time.get_ticks() / 1000.0
	slowness = 1
	while sim_time + slowness * constants.dt <= now_time:
		sim_time += slowness * constants.dt
		objects.update_obj_list()
		objects.space.collide(None, near_callback)
		#objects.world.quickStep(constants.dt)
		objects.world.step(constants.dt)
		objects.contactgroup.empty()
		for i in objects.obj_list:
			i.update()
