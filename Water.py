# implementation of method described http://freespace.virgin.net/hugo.elias/graphics/x_water.htm

import pygame.draw
import math

import objects
import render

def clamp(x):
	if x < 0: return 0
	elif x > 255: return 255
	else: return x

class Water(objects.Thing):
	def __init__(self, size = 15, width = render.WIDTH, height = render.HEIGHT):
		objects.Thing.__init__(self)
		self.size = size; self.width = int(math.ceil(width/float(size))); self.height = int(math.ceil(height/float(size)))
		self.a1 = [[0. for x in range(self.width)] for y in range(self.height)]
		self.a2 = [[0. for x in range(self.width)] for y in range(self.height)]
		pass
	
	def update(self):
		for y in range(1, self.height-1):
			for x in range(1, self.width-1):
				a1 = self.a1
				self.a2[y][x] = 0.3 * (a1[y][x-1] + a1[y][x+1] + a1[y-1][x] + a1[y+1][x])/2 - self.a2[y][x]
				self.a2[y][x] *= 0.99
		temp = self.a1
		self.a1 = self.a2
		self.a2 = temp
		pass
	
	def draw(self):
		for y in range(0, self.height):
			for x in range(0, self.width):
				s = pygame.Surface((self.size, self.size))
				s.set_alpha(128)
				s.fill((0, 0, clamp(int(self.a1[y][x]/2+128)), 250))
				render.screen.blit(s, (x * self.size, y * self.size))
		pass
