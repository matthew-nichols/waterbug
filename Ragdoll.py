from math import *
import ode
def len3(v):
    """Returns the length of 3-vector v."""
    return sqrt(v[0]**2 + v[1]**2 + v[2]**2)
def add3(a, b):
    """Returns the sum of 3-vectors a and b."""
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub3(a, b):
    """Returns the difference between 3-vectors a and b."""
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul3(v, s):
    """Returns 3-vector v multiplied by scalar s."""
    return (v[0] * s, v[1] * s, v[2] * s)
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

class RagDoll():
    def __init__(self, world, space, density, offset = (0.0, 0.0, 0.0)):
        """Creates a ragdoll of standard size at the given offset."""
        self.i = 0
        self.world = world
        self.space = space
        self.density = density
        self.bodies = []
        self.geoms = []
        self.joints = []
        self.totalMass = 0.0

        self.offset = offset
        self.bodies2 = []
        self.geoms2 = []

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
##        self.segment2 = self.customBody(self.part1, self.part2, self.radius)
        ##(z, y, x)
        
        
        self.segment10 = self.customBody((0.0, 0.0, 1.0), (0.0, 0.0, 0.0), 0.1)
##        self.joint10 = self.makeJoint(self.segment10, None, (0.0, 0.0, 0.5))
        
        self.segment2 = self.customBody((0.1, 0.0, 1.6), (0.1, 0.0, 2.0), self.radius)
        self.segment3 = self.customBody((0.1, 0.0, 1.0), (0.1, 0.0, 1.5), self.radius)
        self.joint2 = self.makeJoint(self.segment2, self.segment3, (0.1, 0.0, 1.55))
        self.joint3 = self.makeJoint(self.segment3, self.segment10, (0.1, 0.0, 1.0))
                
        self.segment4 = self.customBody((-0.1, 0.0, 1.6), (-0.1, 0.0, 2.0), self.radius)
        self.segment5 = self.customBody((-0.1, 0.0, 1.0), (-0.1, 0.0, 1.5), self.radius)
        self.joint4 = self.makeJoint(self.segment4, self.segment5, (-0.1, 0.0, 1.55))
        self.joint5 = self.makeJoint(self.segment5, self.segment10, (-0.1, 0.0, 1.0))

        self.segment6 = self.customBody((0.1, 0.0, -0.6), (0.1, 0.0, -1.0), self.radius)
        self.segment7 = self.customBody((0.1, 0.0,  0.0), (0.1, 0.0, -0.5), self.radius)
        self.joint6 = self.makeJoint(self.segment6, self.segment7, (0.1, 0.0, -0.55))
        self.joint7 = self.makeJoint(self.segment7, self.segment10, (0.1, 0.0, 0.0))

        self.segment8 = self.customBody((-0.1, 0.0, -0.6), (-0.1, 0.0, -1.0), self.radius)
        self.segment9 = self.customBody((-0.1, 0.0,  0.0), (-0.1, 0.0, -0.5), self.radius)
        self.joint8 = self.makeJoint(self.segment8, self.segment9, (-0.1, 0.0, -0.55))
        self.joint9 = self.makeJoint(self.segment9, self.segment10, (-0.1, 0.0, 0.0))

############Obstacles##############
##        self.segment11 = self.customBody((0.1, 1.0, -1.0), (0.1, 1.0, -1.7), 0.25)
##        self.joint11 = self.makeJoint2(self.segment11, None, (0.1, 1.0, -1.0))
        self.segment11 = self.customBody((0.0, 1.0, -1.0), (0.0, 1.0, -1.7), 0.25)
        n = ode.Mass()
##        n.adjust(200)
##        print m
        n.setCapsuleTotal(1000, 3, 0.25, dist3((0.0, 1.0, -1.0), (0.0, 1.0, -1.7)))
        self.segment11.setMass(n)
        ##build a class of invisible joints to the end of the legs, push and pull from that. 
        self.joint11 = self.makeJoint2(self.segment11, None, (0.0, 1.0, -1.0))

        self.segment12 = self.customBody((0.0, 0.0, 2.5), (0.0, 1.0, 2.5), 0.15)
        self.joint12 = self.makeJoint2(self.segment12, None, (0.0, 0.0, 2.5))
        self.segment13 = self.customBody((-1.0, 0.0, 1.5), (-1.0, 1.0, 1.5), 0.15)
        self.joint13 = self.makeJoint2(self.segment13, None, (0.0, 0.0, 1.5))
        self.segment14 = self.customBody((1.0, 0.0, -1.5), (1.0, 1.0, -1.5), 0.15)
        self.joint14 = self.makeJoint2(self.segment14, None, (0.0, 0.0, -1.5))
        ####add a little noise/push####
##        self.joint0.addTorque(500)
##        self.joint1.addTorque(100)
##        self.segment2.addTorque([0.5, 0, 0])
        self.segment11.addTorque([-50000.0, 0, 0])

    def customBody(self, p1, p2, radius):
        cyllen = dist3(p1, p2)
        body = ode.Body(self.world)
        m = ode.Mass()
        m.setCapsule(self.density, 3, radius, cyllen)
        body.setMass(m)
        body.shape = "capsule"
        body.length = cyllen
        body.radius = radius
        geom = ode.GeomCCylinder(self.space, radius, cyllen)
        geom.setBody(body)
        body.setPosition(mul3(add3(p1, p2), 0.5))

        za = norm3(sub3(p2, p1))
        if (abs(dot3(za, (1.0, 0.0, 0.0))) < 0.7): xa = (1.0, 0.0, 0.0)
        else: xa = (0.0, 1.0, 0.0)
        ya = cross(za, xa)
        xa = norm3(cross(ya, za))
        ya = cross(za, xa)
        rot = (xa[0], ya[0], za[0], xa[1], ya[1], za[1], xa[2], ya[2], za[2])

        body.setPosition(mul3(add3(p1, p2), 0.5))
        body.setRotation(rot)
        
        self.bodies.append(body)
        self.geoms.append(geom)
        self.totalMass += body.getMass().mass
        return body
        
    def customBody2(self, p1, p2):
        body = ode.Body(self.world)
        m = ode.Mass()
        m.adjust(100000)
        p = dist3(p1, p2)
        lx = abs(p2[0] - p1[0])
        ly = abs(p2[1]-p1[1])
        lz = abs(p2[2] - p1[2])
        m.setBox(90000, lx, ly, lz)
        body.setMass(m)
        body.shape = "box"
        body.boxsize = (lx, ly, lz)
##        p3 = (p1[0], p1[1], (p2[2]+p1[2])/2.0+0.04)
##        body.setPosition(p3)

        geom = ode.GeomBox(self.space, lengths=body.boxsize)
        geom.setBody(body)
        
        self.bodies2.append(body)
        self.geoms2.append(geom)
        
        self.totalMass += body.getMass().mass

    def makeJoint(self, seg1, seg2, anchor):
        self.joint = ode.HingeJoint(self.world)
        self.joint.attach(seg1, seg2)
        self.joint.setAnchor(anchor)
        self.joint.setAxis((0, 1, 0))
        self.joints.append(self.joint)
        return self.joint
    
    def makeJoint2(self, seg1, seg2, anchor):
        self.joint = ode.HingeJoint(self.world)
        self.joint.attach(seg1, seg2)
        self.joint.setAnchor(anchor)
        self.joints.append(self.joint)
        return self.joint

    def applyTorque(self, angle, angVel, wantedAngle, f, b, segment):
        torque = f*(wantedAngle-angle)+b*(0 - angVel[0])
        ragdoll.segment.addTorque([torque, 0, 0])
    
##world = ode.World()
####world.setGravity((0.0, -9.81, 0.0))
##world.setERP(0.1)
##world.setCFM(1E-4)
##space = ode.Space()
##ragdoll = RagDoll(world, space, 500, (0.0, 0.0, 0.0))
