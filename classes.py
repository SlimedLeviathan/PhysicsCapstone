# this file contains all of the main classes

# all angles are in degrees

import math

# normal for gravity, but can be changed in the program
gravity = 9.8 # this is also here since it should be the farthest down import

boxSize = 50

boxes = []

class Box:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.angle = 0 # if the box is on an angle, this will change to change the rotation of the box on the screen

        self.setPoints()

        self.speed = [0, 0] # speed on each axis

        self.forces = [] # list of all of the forces acting on this box

        # all boxes have the gravitational force applied to them

        self.addForce(Force(gravity, "g"))

        boxes.append(self)

    def applyForces(self):
        netForce = [0, 0]

        for force in self.forces:
            netForce = force.applyForce(netForce)

        # we divide by 1000 since the measurements are in m/s and we are doing this every millisecond, so we have to change it a bit
        self.speed[0] += netForce[0] / 1000
        self.speed[1] += netForce[1] / 1000

    def setPoints(self):
        if (self.angle != 0):
            widthX = boxSize / math.cos(self.angle)
            widthY = boxSize / math.sin(self.angle)

            heightX = boxSize / math.sin(self.angle)
            heightY = boxSize / math.cos(self.angle)

        else:
            widthX = boxSize
            widthY = 0

            heightX = 0
            heightY = boxSize

        self.points = [[self.x, self.y], [self.x + widthX, self.y + widthY], [self.x + widthX + heightX, self.y + widthY + heightY], [self.x + heightX, self.y + heightY],]

    def move(self):
        self.applyForces()

        self.x += self.speed[0]
        self.y += self.speed[1]

        self.setPoints()

    def addForce(self, force):
        self.forces.append(force)

platforms = []

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.points = [[x, y], [x + width, y], [x + width, y + height], [x, y + height]]

        self.forceAttachments = [] # all of the forces attached to this platform

        platforms.append(self)

    def addNorm(self):
        return Force(gravity, "n", 180)


class Incline(Platform):
    def __init__(self, x, y, width, angle):

        self.angle = angle
        
        height = abs(width) / math.tan(math.radians(angle)) # finds the height of our triangle

        Platform.__init__(x, y, width, height)

        self.points = [[x, y], [x + width, y], [x + width, y + height]]

    def addNorm(self):
        # this add norm is a bit different since the box would be sitting on it at an angle

        return Force(gravity, "n", self.angle + 180)
    

class Force:
    def __init__(self, magnitude, char, dir = 0):
        self.magnitude = magnitude
        self.char = char

        self.dir = dir # dir should be an angle, where 0 would be down

    def setMag(self, mag):
        self.magnitude = mag

    def applyForce(self, netForce):
        # find the magnitude in each direction

        if (self.dir != 0):
            xForce = self.magnitude / math.sin(math.radians(self.dir))
            yForce = self.magnitude / math.cos(math.radians(self.dir))
        
        else:
            yForce = self.magnitude
            xForce = 0

        netForce[0] += xForce
        netForce[1] += yForce

        return netForce # returns the netForces

class ForceObject:
    def __init__(self, magnitude, char, dir):
        self.force = Force(magnitude, char, dir)

        self.maxMagnitude = magnitude

class String(ForceObject):
    def __init__(self, maxMagnitude, dir):
        ForceObject.__init__(maxMagnitude, "t", dir) # it uses tension force

class Spring(ForceObject):
    def __init__(self, maxMagnitude, dir):
        ForceObject.__init__(maxMagnitude, "s", dir)