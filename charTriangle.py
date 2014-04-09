import math
from math import *
import objects
import render

import ode

def sign(x):
    """Returns 1.0 if x is positive, -1.0 if x is negative or zero."""
    if x > 0.0: return 1.0
    else: return -1.0

def len3(v):
    """Returns the length of 3-vector v."""
    return sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def neg3(v):
    """Returns the negation of 3-vector v."""
    return (-v[0], -v[1], -v[2])

def add3(a, b):
    """Returns the sum of 3-vectors a and b."""
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def sub3(a, b):
    """Returns the difference between 3-vectors a and b."""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def mul3(v, s):
    """Returns 3-vector v multiplied by scalar s."""
    return (v[0] * s, v[1] * s, v[2] * s)

def div3(v, s):
    """Returns 3-vector v divided by scalar s."""
    return (v[0] / s, v[1] / s, v[2] / s)

def dist3(a, b):
    """Returns the distance between point 3-vectors a and b."""
    return len3(sub3(a, b))

def norm3(v):
    """Returns the unit length 3-vector parallel to 3-vector v."""
    l = len3(v)
    if (l > 0.0): return (v[0] / l, v[1] / l, v[2] / l)
    else: return (0.0, 0.0, 0.0)

def dot3(a, b):
    """Returns the dot product of 3-vectors a and b."""
    return (a[0] * b[0] + a[1] * b[1] + a[2] * b[2])

def cross(a, b):
    """Returns the cross product of 3-vectors a and b."""
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0])

def project3(v, d):
    """Returns projection of 3-vector v onto unit 3-vector d."""
    return mul3(v, dot3(norm3(v), d))

def acosdot3(a, b):
    """Returns the angle between unit 3-vectors a and b."""
    x = dot3(a, b)
    if x < -1.0: return pi
    elif x > 1.0: return 0.0
    else: return acos(x)

def rotate3(m, v):
    """Returns the rotation of 3-vector v by 3x3 (row major) matrix m."""
    return (v[0] * m[0] + v[1] * m[1] + v[2] * m[2],
        v[0] * m[3] + v[1] * m[4] + v[2] * m[5],
        v[0] * m[6] + v[1] * m[7] + v[2] * m[8])

def invert3x3(m):
    """Returns the inversion (transpose) of 3x3 rotation matrix m."""
    return (m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8])

def zaxis(m):
    """Returns the z-axis vector from 3x3 (row major) rotation matrix m."""
    return (m[2], m[5], m[8])

def calcRotMatrix(axis, angle):
    """
    Returns the row-major 3x3 rotation matrix defining a rotation around axis by
    angle.
    """
    cosTheta = cos(angle)
    sinTheta = sin(angle)
    t = 1.0 - cosTheta
    return (
        t * axis[0]**2 + cosTheta,
        t * axis[0] * axis[1] - sinTheta * axis[2],
        t * axis[0] * axis[2] + sinTheta * axis[1],
        t * axis[0] * axis[1] + sinTheta * axis[2],
        t * axis[1]**2 + cosTheta,
        t * axis[1] * axis[2] - sinTheta * axis[0],
        t * axis[0] * axis[2] - sinTheta * axis[1],
        t * axis[1] * axis[2] + sinTheta * axis[0],
        t * axis[2]**2 + cosTheta)

class RagDoll(objects.Thing):
    def __init__(self, world, space, density, scale = 1, offset = (0.0, 0.0)):
        """Creates a ragdoll of standard size at the given offset."""
        self.i = 0
        self.world = world
        self.space = space
        #self.density = density
        self.bodies = []
        self.geoms = []
        self.joints = []
        self.totalMass = 0.0

        self.offsetx, self.offsety = offset
        self.scale = scale
        self.bodies2 = []
        self.geoms2 = []

        self.wantedAngle1 = 0
        self.wantedAngle2 = 0
        self.wantedAngle3 = 0
        self.wantedAngle4 = 0
        self.wantedAngle5 = 0
        self.wantedAngle6 = 0
        self.wantedAngle7 = 0
        self.wantedAngle8 = 0
        self.wantedAngle9 = 0
        self.wantedAngle10 = 0
        self.wantedAngle11 = 0
        
        self.radius = 0.05
        objects.Thing.__init__(self)
        
    def construct(self):
        self.segment1 = self.customBody((0.25, 0.0, 0.0), (-0.25, 0.0, 0.0), self.radius)
        self.segment2 = self.customBody((0.3, 0.0, 0.0), (0.8, 0.0, 0.0), self.radius)
        self.segment3 = self.customBody((-0.3, 0.0, 0.0), (-0.8, 0.0, 0.0), self.radius)

        self.joint1 = self.makeJoint(self.segment2, self.segment1, (0.25, 0.0, 0.0))
        self.joint2 = self.makeJoint(self.segment3, self.segment1, (-0.25, 0.0, 0.0))
##        self.joint3 = self.makeJoint(self.segment1, self.segment3, (0.01, 0.0, 0.01))

    def customBody(self, p1, p2, radius):
        p1_x, _, p1_y = p1
        p2_x, _, p2_y = p2
        p1_x = p1_x * self.scale + self.offsetx
        p1_y = p1_y * self.scale + self.offsety
        p2_x = p2_x * self.scale + self.offsetx
        p2_y = p2_y * self.scale + self.offsety
        radius *= self.scale
        body = objects.Capsule( ( (p1_x + p2_x)/2, (p1_y + p2_y)/2 ), radius, math.sqrt( (p1_x - p2_x)**2 + (p1_y - p2_y)**2 ), 1, math.atan2(p2_y - p1_y, p2_x - p1_x))
        objects.construct_now(body)
        self.totalMass += 1
        self.bodies.append(body)
        return body

    def makeJoint(self, seg1, seg2, anchor):
        self.joint = ode.HingeJoint(self.world)
        self.joint.attach(seg1.body, seg2.body)
        x, _, y = anchor
        x = x * self.scale + self.offsetx; y = y * self.scale + self.offsety
        self.joint.setAnchor((x,y,0))
        self.joint.setAxis((0, 0, 1))
        self.joints.append(self.joint)
        return self.joint
    
    def makeJoint2(self, seg1, seg2, anchor):
        return None
        self.joint = ode.HingeJoint(self.world)
        self.joint.attach(seg1, seg2)
        self.joint.setAnchor(anchor)
        self.joints.append(self.joint)
        return self.joint
    
    def addTorque(self, torque):
        self.segment10.addTorque(torque)
    
    def update(ragdoll):
        angle1 = ragdoll.joint1.getAngle()
        angle2 = ragdoll.joint2.getAngle()
        angularVelocity1 = ragdoll.joint1.getAngleRate()
        angularVelocity2 = ragdoll.joint2.getAngleRate()
        d = 0.3
        u = 0.9
        torque1 = u*(ragdoll.wantedAngle1 - angle1) + d*(0 - angularVelocity1)
        torque2 = u*(ragdoll.wantedAngle2 - angle2) + d*(0 - angularVelocity2)
##        ragdoll.segment1.addTorque([0, torque1, 0])
##        ragdoll.segment2.addTorque([0, torque1, 0])
##        ragdoll.segment3.addTorque([0, torque2, 0])
        ragdoll.joint1.addTorque(torque1)
        ragdoll.joint2.addTorque(torque2)
    
    def draw(self):
        for i in self.joints:
            render.drawPoint(i.getAnchor(), render.green)
    
    def setWantedPosition(ragdoll, pos):
        if pos == 0:
            ragdoll.wantedAngle1 = 0
            ragdoll.wantedAngle2 = 0
            
        elif pos == 1:
            ragdoll.wantedAngle1 = pi/1.5
            ragdoll.wantedAngle2 = pi/1.5
        elif pos == 2:
            ragdoll.wantedAngle2 = -pi/3
            
    def addForce(self, force):
        pass

