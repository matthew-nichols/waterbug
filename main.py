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

#water = Water.Water()
#objects.construct_now(water)

running = 1
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

box = objects.Ball((2.5, 0.5),0.1)
def thisCollision(other):
	if other is not None and getattr(other, 'tag', '') == 'player':
		print "Ball & Player!"
	return True
box.onCollision = thisCollision

#objects.Box((0.7,0.5),(0.2,0.2))
#objects.Box((0.3,0.5),(0.3,0.3))
#objects.Ball((1.3,1.3),0.2)
#cannon.Cannon((3.5,3.5),(1,0.2))
objects.Capsule((1.7,1.7),0.04,0.4)
ragdoll = Ragdoll.RagDoll(objects.world, objects.space, 1, 0.3, (0.3, 0.5))
objects.construct_now(ragdoll)
ragdoll.addTorque(10)
ragdoll2 = Ragdoll.RagDoll(objects.world, objects.space, 1, 0.3, (0.3+5, 0.5))
objects.construct_now(ragdoll2)
ragdoll2.addTorque(10)

ragdoll.tag = 'player'
ragdoll2.tag = 'player'
#characterThree = charThree.RagDoll(objects.world, objects.space, 1, 0.3, (1.5, 0.5))
#objects.construct_now(characterThree)
#characterBox = charBox.RagDoll(objects.world, objects.space, 1, 0.3, (0.5, 1.5))
#objects.construct_now(characterBox)
characterTriangle = charTriangle.RagDoll(objects.world, objects.space, 1, 0.3, (1.5, 1.5))
#objects.construct_now(characterTriangle)
characterTriangle2 = charTriangle.RagDoll(objects.world, objects.space, 1, 0.3, (1.5+5, 1.5))
#characterTwo = charTwo.RagDoll(objects.world, objects.space, 1, 0.3, (2.5, 1.5))
#objects.construct_now(characterTwo)
while running:
	e = event.poll()
	if e.type == pygame.QUIT:
		running = 0
	if e.type == pygame.KEYDOWN:
		if e.key == pygame.K_q:
			running = False; break
		elif e.key == pygame.K_UP:
			box.addForce((0,-100))
		elif e.key == pygame.K_DOWN:
			box.addForce((0,100))
		elif e.key == pygame.K_LEFT:
			box.addForce((-100,0))
		elif e.key == pygame.K_RIGHT:
			box.addForce((100,0))
		elif e.key == pygame.K_w:
			box.addTorque(1)
		elif e.key == pygame.K_e:
			box.addTorque(-1)
		elif e.key == pygame.K_a:
			ragdoll.setWantedPosition(0)
		elif e.key == pygame.K_s:
			ragdoll.setWantedPosition(1)
		elif e.key == pygame.K_k:
			ragdoll2.setWantedPosition(0)
		elif e.key == pygame.K_l:
			ragdoll2.setWantedPosition(1)
		elif e.key == pygame.K_x:
			for i in objects.obj_list:
				if hasattr(i, 'addForce'):
					i.addForce((100,0))
#		elif e.key == pygame.K_c:
#			characterThree.setWantedPosition(0)
#		elif e.key == pygame.K_v:
#			characterThree.setWantedPosition(1)
#		elif e.key == pygame.K_b:
#			characterThree.setWantedPosition(2)
#		elif e.key == pygame.K_n:
#			characterBox.setWantedPosition(0)
#		elif e.key == pygame.K_m:
#			characterBox.setWantedPosition(1)
		elif e.key == pygame.K_1:
			characterTriangle.setWantedPosition(0)
		elif e.key == pygame.K_2:
			characterTriangle.setWantedPosition(1)
		elif e.key == pygame.K_3:
			characterTriangle.setWantedPosition(2)
		elif e.key == pygame.K_4:
			characterTriangle.setWantedPosition(5)
		elif e.key == pygame.K_5:
			characterTriangle.setWantedPosition(6)
		elif e.key == pygame.K_6:
			characterTriangle2.setWantedPosition(0)
		elif e.key == pygame.K_7:
			characterTriangle2.setWantedPosition(1)
		elif e.key == pygame.K_8:
			characterTriangle2.setWantedPosition(2)
		elif e.key == pygame.K_9:
			characterTriangle2.setWantedPosition(5)
		elif e.key == pygame.K_0:
			characterTriangle2.setWantedPosition(6)
#		elif e.key == pygame.K_8:
#			characterTwo.setWantedPosition(0)
#		elif e.key == pygame.K_9:
#			characterTwo.setWantedPosition(1)
	# FIXME: for some reason, this causes lag when mouse is moving
	#if e.type == pygame.MOUSEMOTION:
	#	water.a1[e.pos[1]/water.size][e.pos[0]/water.size] = 255;
			
	render.screen.fill((0,0,0))
	#for i in objects.space:
	#	render.drawGeom(i)
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
