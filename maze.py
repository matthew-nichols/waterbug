#!/usr/bin/env python2.7
# encoding: utf8

import random
import sys
import ode

import render
import objects

# thing which holds static maze
class Maze(objects.Thing):
	def __init__(self, width = 4, height = 4):
		objects.Thing.__init__(self)
		self.width = width
		self.height = height
	
	def draw(self):
		for geom in self.geoms:
			render.drawGeom(geom)
	
	def destroy(self):
		for geom in self.geoms:
			geom.getSpace().remove(geom)
		del self.geoms
	
	def generate_random(self):
		self.rows = [ [random.choice([0,1]) for x in range(self.width)] for y in range(self.height+1) ]
		self.cols = [ [random.choice([0,1]) for x in range(self.width+1)] for y in range(self.height) ]
		# start always at y=0, end at y=height-1
		self.start = random.randint(0, self.width - 1)
		self.end = random.randint(0, self.width - 1)
		
		for x in xrange(self.width):
			if x != self.start:
				self.rows[0][x] = 1
			else:
				self.rows[0][x] = 0
			if x != self.end:
				self.rows[self.height][x] = 1
			else:
				self.rows[self.height][x] = 0
		for y in xrange(self.height):
			self.cols[y][0] = 1
			self.cols[y][self.width] = 1	
		
	def generate_simple(self):
		self.generate_random()	
		
		overlapping = self.overlapping_set()
		for l in overlapping.values():
			x,y,t = random.choice(l)
			if t == "col":
				self.cols[y][x] = 0
			elif t == "row":
				self.rows[y][x] = 0
	
	def generate_simple2(self):
		self.generate_random()
		
		overlapping = self.overlapping_set()
		while len(overlapping) > 0:
			x,y,t = random.choice(random.choice(overlapping.values()))
			if t == "col":
				self.cols[y][x] = 0
			elif t == "row":
				self.rows[y][x] = 0
			overlapping = self.overlapping_set()
	
	def overlapping_set(self):
		spaces = [ [0 for x in range(self.width)] for y in range(self.height) ]
		number = 1
		def mark_space(x, y):
			spaces[y][x] = number
			if y != 0 and spaces[y-1][x] == 0 and self.rows[y][x] == 0:
				mark_space(x, y-1)
			if x != 0 and spaces[y][x-1] == 0 and self.cols[y][x] == 0:
				mark_space(x-1, y)
			if x != self.width - 1 and spaces[y][x+1] == 0 and self.cols[y][x+1] == 0:
				mark_space(x+1, y)
			if y != self.height - 1 and spaces[y+1][x] == 0 and self.rows[y+1][x] == 0:
				mark_space(x, y+1)			
		
		for y in xrange(self.height):
			for x in xrange(self.width):
				if spaces[y][x] == 0:
					mark_space(x, y)
					number += 1
		
		overlapping = {}
		def add_to_overlapping(s1, s2, x, y, t):
			if s1 != s2:
				index = (min(s1,s2),max(s1,s2))
				if index in overlapping:
					overlapping[index].append((x,y,t))
				else:
					overlapping[index] = [(x,y,t)]
		
		# find rows that divide different areas
		for y in xrange(1,self.height):
			for x in xrange(0,self.width):
				add_to_overlapping(spaces[y-1][x], spaces[y][x], x, y, "row")
		
		# find cols
		for y in xrange(0,self.height):
			for x in xrange(1,self.width):
				add_to_overlapping(spaces[y][x-1], spaces[y][x], x, y, "col")
		return overlapping
	
	def prin(self):
		for y in xrange(self.height):
			for x in xrange(self.width):
				if self.rows[y][x]:
					sys.stdout.write("┼─")
				else:
					sys.stdout.write("┼ ")
			print "┼"
			for x in xrange(self.width+1):
				if self.cols[y][x]:
					sys.stdout.write("│ ")
				else:
					sys.stdout.write("  ")
			print
		for x in xrange(self.width):
			if self.rows[self.height][x]:
				sys.stdout.write("┼─")
			else:
				sys.stdout.write("┼ ")
		print "┼"
				
	def make_geoms(self, space, half_width = 0.1):
		self.geoms = []
		y = 0
			
		for x in xrange(self.width+1):
			y = 0
			while y < self.height:
				y_begin = y
				while y < self.height and self.cols[y][x] == 1:
					y += 1
				if y - y_begin != 0:
					geom = ode.GeomBox(space, (2 * half_width, y - y_begin + 2 * half_width, half_width))
					geom.setPosition((x, float(y + y_begin) / 2, 0))
					self.geoms.append(geom)
				while y < self.height and self.cols[y][x] == 0:
					y += 1
		for y in xrange(self.height+1):
			x = 0
			while x < self.width:
				x_begin = x
				if y < self.height and self.cols[y][x] == 1 or y > 0 and self.cols[y-1][x] == 1:
					include_first = False
				else:
					include_first = True
					
				def cond(): return (y < self.height and self.cols[y][x+1] == 1) or (y > 0 and self.cols[y-1][x+1] == 1)
					
				while x < self.width and self.rows[y][x] == 1 and not cond():
					x += 1
					
				if self.rows[y][x] == 1 and cond():
					x += 1
					include_second = False
				elif self.rows[y][x] == 1:
					x += 1
					include_second = True
				else:
					include_second = True
				
				if x - x_begin != 0:
					if include_first:
						x_first = x_begin - half_width
					else:
						x_first = x_begin + half_width
					if include_second:
						x_last = x + half_width
					else:
						x_last = x - half_width
					geom = ode.GeomBox(space, (x_last - x_first, 2 * half_width, half_width))
					geom.setPosition(((x_first + x_last) / 2, y, 0))
					self.geoms.append(geom)
				
				while x < self.width and self.rows[y][x] == 0:
					x += 1

#maze = Maze(4,5)
#maze.prin()
