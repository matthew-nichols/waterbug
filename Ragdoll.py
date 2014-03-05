import math
from math import *
import objects

import ode

class RagDoll(objects.Thing):
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
        objects.Thing.__init__(self)
        
    def construct(self):
        self.segment10 = self.customBody((0.0, 0.0, 1.0), (0.0, 0.0, 0.0), 0.1)
        
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

    def customBody(self, p1, p2, radius):
        p1_x, _, p1_y = p1
        p2_x, _, p2_y = p2        
        body = objects.Capsule( ( (p1_x + p2_x)/2, (p1_y + p2_y)/2 ), radius, math.sqrt( (p1_x - p2_x)**2 + (p1_y - p2_y)**2 ), 1, math.atan2(p2_y - p1_y, p2_x - p1_x))
        objects.construct_now(body)
        self.totalMass += 1
        return body

    def makeJoint(self, seg1, seg2, anchor):
        self.joint = ode.HingeJoint(self.world)
        self.joint.attach(seg1.body, seg2.body)
        x, _, y = anchor
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

    def applyTorque(self, angle, angVel, wantedAngle, f, b, segment):
        torque = f*(wantedAngle-angle)+b*(0 - angVel[0])
        ragdoll.segment.addTorque([torque, 0, 0])

