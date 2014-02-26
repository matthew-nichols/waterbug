import ode
import pygame
import pygame.display as display
import pygame.draw as draw
import pygame.gfxdraw as gfxdraw
import pygame.time
from pygame import Color
import math

WIDTH = 640
HEIGHT = 640

pygame.init()
screen = display.set_mode((WIDTH,HEIGHT))

red = Color(255,0,0)
green = Color(0,255,0)
blue = Color(0,0,255)

the_denom = 5
# automate these and make them less ridiculous
def to_screen_pnt(x, y):
	return (x*WIDTH/the_denom+50, y*HEIGHT/the_denom+50)
def to_screen_vec(x, y):
	return (x*WIDTH/the_denom, y*HEIGHT/the_denom)
def to_screen_len(r):
	return r*WIDTH/the_denom

def drawGeom(geom):
	if type(geom) is ode.GeomBox:
		x, y, _ = geom.getPosition()
		a, b, _ = geom.getLengths()
		r = geom.getRotation()
		costheta = r[0]; sintheta = r[1]
		p1 = to_screen_pnt(x + a/2 * costheta + b/2 * sintheta, y - a/2 * sintheta + b/2 * costheta)
		p2 = to_screen_pnt(x + a/2 * costheta - b/2 * sintheta, y - a/2 * sintheta - b/2 * costheta)
		p3 = to_screen_pnt(x - a/2 * costheta - b/2 * sintheta, y + a/2 * sintheta - b/2 * costheta)
		p4 = to_screen_pnt(x - a/2 * costheta + b/2 * sintheta, y + a/2 * sintheta + b/2 * costheta)
		draw.lines(screen, blue, True, [p1, p2, p3, p4])
		#drawLine((x,y),(x+a/2*costheta,y-a/2*sintheta))
	elif type(geom) is ode.GeomSphere:
		x, y, _ = geom.getPosition()
		r = geom.getRadius()
		rotmat = geom.getRotation()
		costheta = rotmat[0]; sintheta = rotmat[1]
		px, py = to_screen_pnt(x, y)
		pr = to_screen_len(r)
		draw.circle(screen, blue, (int(px), int(py)), int(pr), 1)
		drawLine((x,y), (x + costheta * r, y - sintheta * r))
	elif type(geom) is ode.GeomCapsule:
		pass
	elif isinstance(geom, ode.SpaceBase):
		for i in geom:
			drawGeom(i)
	else:
		assert False

def drawLine(p1, p2, color = blue):
	x = p1[0]; y = p1[1]
	q = p2[0]; w = p2[1]
	px, py = to_screen_pnt(x, y)
	pq, pw = to_screen_pnt(q, w)
	draw.line(screen, color, (int(px), int(py)), (int(pq), int(pw)))

def drawPoint(p, c = red, r = 5):
	x = p[0]; y = p[1]
	px, py = to_screen_pnt(x, y)
	draw.circle(screen, c, (int(px), int(py)), r, 0)

def drawAnchor(joint):
	p1 = joint.getAnchor()
	p2 = joint.getAnchor2()
	drawPoint(p1, red)
	drawPoint(p2, green)
