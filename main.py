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

running = 1

the_maze = maze.Maze(4,4)
the_maze.generate_simple2()
the_maze.make_geoms(objects.space)

ball_width = 0.05

def near_callback(args, g1, g2):
	if g1.isSpace() or g2.isSpace():
		if g1.isSpace():
			g1.collide(args, near_callback)
		if g2.isSpace():
			g2.collide(args, near_callback)
		ode.collide2(g1, g2, args, near_callback)
	contacts = ode.collide(g1, g2)
	d1 = getattr(g1, 'data', None)
	d2 = getattr(g2, 'data', None)
	# TODO: if d1 and/or d2 are not None, use them to handle collision
	for c in contacts:
		c.setBounce(0.8)
		c.setMu(50)
		j = ode.ContactJoint(objects.world, objects.contactgroup, c)
		j.attach(g1.getBody(), g2.getBody())

sim_time = pygame.time.get_ticks() / 1000.0
		
box = objects.Ball((0.5,0.5),0.1)
#objects.Box((0.7,0.5),(0.2,0.2))
#objects.Box((0.3,0.5),(0.3,0.3))
#objects.Ball((1.3,1.3),0.2)
#cannon.Cannon((3.5,3.5),(1,0.2))
objects.Capsule((1.7,1.7),0.1,0.4)

while running:
	e = event.poll()
	if e.type == pygame.QUIT:
		running = 0
	if e.type == pygame.KEYDOWN:
		if e.key == pygame.K_UP:
			box.addForce((0,-100))
		elif e.key == pygame.K_DOWN:
			box.addForce((0,100))
		elif e.key == pygame.K_LEFT:
			box.addForce((-100,0))
		elif e.key == pygame.K_RIGHT:
			box.addForce((100,0))
		elif e.key == pygame.K_e:
			geom3.disable()
		elif e.key == pygame.K_r:
			geom3.enable()
		elif e.key == pygame.K_q:
			box.addTorque(1)
		elif e.key == pygame.K_w:
			box.addTorque(-1)
		elif e.key == pygame.K_d:
			box.destruct()
		elif e.key == pygame.K_f:
			print pygame.time.get_ticks(), objgraph.by_type('ode.Plane2DJoint')
			
	render.screen.fill((0,0,0))
	#for i in objects.space:
	#	render.drawGeom(i)
	objects.update_obj_list()
	for i in objects.obj_list:
		i.draw()
	
	display.flip()
	
	now_time = pygame.time.get_ticks() / 1000.0
	while sim_time + 5*constants.dt <= now_time:
		sim_time += 5*constants.dt
		objects.update_obj_list()
		objects.space.collide(None, near_callback)
		objects.world.quickStep(constants.dt)
		objects.contactgroup.empty()
		for i in objects.obj_list:
			i.update()
