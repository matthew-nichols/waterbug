#!/usr/bin/env python2.7

import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.event as event
import pygame.gfxdraw as gfxdraw
import pygame.time
from pygame import Color
import ode
import math
import objgraph

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

ball_width = 0.05

def near_callback(args, g1, g2):
	try:
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

the_pickup = Pickup.Pickup((3.5, 3.5), 5, Pickup.XFactor)
strength = Pickup.Pickup((2.5, 2.5), 5, Pickup.Strength)

ragdoll.tag = 'player'
ragdoll2.tag = 'player'

helper1 = Helper.Helper((0.5, 2.5))
helper2 = Helper.Helper((5.5, 2.5))
helper1.tag = 'helper'
helper2.tag = 'helper'

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
