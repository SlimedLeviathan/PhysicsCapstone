# this file contains all of the main classes

# all angles are in degrees

import math

# global variables
# normal for gravity, but can be changed in the program
gravity = 9.8 # this is also here since it should be the farthest down import
airDens = 1.204

boxSize = 50

boxes = []

# returns false if min and max are both greater than or less than the point
def minMaxDetect(point, min, max): # each parameter is one int
    if (min > point and max > point):
        return False
    
    elif (min < point and max < point):
        return False

    return True

# secondary helper function to the line collision which does all of the minMaxDetect calls for a single point and a line
def pointLineMinMax(point, line): # point is: [p1, p2], line is: [[p1, p2], [p1, p2]]
    # returns true if the 2 ponts of the line are not both greater than or less than the point

    xDetect = minMaxDetect(point[0], line[0][0], line[1][0])
    yDetect = minMaxDetect(point[1], line[0][1], line[1][1])

    return xDetect and yDetect

# returns trueif the 2 lines inputted collide
def lineCollision(line1, line2): # each line is: [[p11, p12], [p21, p22]]
    # two lines are colliding if their mins and maxes are BOTH greater or less than the others min or max

    line1Detect1 = pointLineMinMax(line2[0], line1)
    line1Detect2 = pointLineMinMax(line2[1], line1)
    line2Detect1 = pointLineMinMax(line1[0], line2)
    line2Detect2 = pointLineMinMax(line1[1], line2)

    return (line1Detect1 and line1Detect2) or (line2Detect1 and line2Detect2)

class Box:
    
    # info for air resistance
    dragCoe = 1.05 # this definetly should change if the box rotates, buuuttt i aint got a clue how to change that
    crossSection = boxSize * boxSize # the crossSectionalArea is just the box size times itself, since this would be a cube

    def __init__(self, x, y, mass = 50):
        self.x = x
        self.y = y

        self.mass = mass

        self.angle = 0 # if the box is on an angle, this will change to change the rotation of the box on the screen

        self.setPoints()

        self.speed = [0, 0] # speed on each axis

        self.forces = [] # list of all of the forces acting on this box

        self.forceObjects = [] # list of all of the force objects acting on this box

        self.collidingPlatforms = [] # all of the platforms currently colliding with the box, structured as :[platform, direction]

        # all boxes have the gravitational force applied to them

        boxes.append(self)

    # returns the value of the normal force
    def getNorm(self):
        return gravity * self.mass

    def addGravity(self):
        self.addForce(Force(self.getNorm(), "g"))

    def getFriction(self, frictionCoe):
        return self.getNorm() * frictionCoe
    
    def getAirResistance(self):
        return .5 * airDens * (self.speed[1] ** 2) * self.dragCoe * self.crossSection

    def applyFriction(self, endForce):
        # basically, we take the speed and forces currently acting on an object in order to make an accurate amount of friction
        # we also make sure the box is touching a platform

        friction = [0, 0]

        ground = False

        for data in self.collidingPlatforms:
            # currently, dont worry aout ow much of the platform is touching the box

            if (data[1] == "up" or data[1] == "down"):
                ground = True

                # find the friction force of the object

                xFriction = self.getFriction(data[0].frictionCoefficient)

                if (self.speed[0] == 0): # static friction
                    if xFriction > endForce[0]:
                        xFriction = endForce[0] # if the static friction is above the endForce, then we make sure it doesnt actually move the box

                if (endForce[0] > 0): # makes sure ti gos the opposite direction
                    xFriction *= -1

                friction[0] += xFriction

            if (data[1] == "left" or data[1] == "right"):
                pass

        # if the box is not touching any platform, and therefore, freefalling (as long as the endForce has some value greater than 0)
        # we calculate the air resistance

        friction[1] -= self.getAirResistance() # Fa
        
        return friction

    def applyForces(self):
        netForce = [0, 0]

        for force in self.forces:
            netForce = force.applyForce(netForce)

        # if the box is touching the ground, and there is a net force, we add the friction force
        # we also take intoaccount the fact that the object might be moving as well, and add that as a force in the friction calcuations
        endForce = [netForce[0], netForce[1]]

        endForce[0] += self.mass * self.speed[0]
        endForce[1] += self.mass * self.speed[1]

        friction = self.applyFriction(endForce)

        netForce[0] += friction[0]
        netForce[1] += friction[1]

        # we divide by 1000 since the measurements are in m/s and we are doing this every millisecond, so we have to change it a bit
        self.speed[0] += (netForce[0] / (self.mass * 1000)) 
        self.speed[1] += (netForce[1] / (self.mass * 1000)) 

        self.forces.clear() # clears the forces, since each millisecond they all need to re-add themselves in order to be relevant
        self.collidingPlatforms.clear()

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

    def collisionDetect(self):
        # checks all platofrms to see which ones this box is touching, then apply the forces
        for platform in platforms:
            if (abs(platform.y - (self.y)) < 1): # if the difference in Ys are less than 1 (so they are touching top to bottom)
                self.addForce(platform.addNorm(self))

                self.collidingPlatforms.append([platform, "down"])

                self.addForce(Force(self.mass * -((self.speed[1] ** 2) * 1000) * .5, "s")) # im just saying spring since it uses the pressure of the object to keep it from falling

    def forceObjectApply(self):
        for forceObject in self.forceObjects:
            pass


    def move(self):
        self.addGravity() # gravity comes first
        
        self.collisionDetect() # then the norms

        self.forceObjectApply() # then the force objects

        self.applyForces() # then we apply the forces

        self.x += self.speed[0]
        self.y += self.speed[1]

        self.setPoints()

    def addForce(self, force):
        self.forces.append(force)

platforms = []

class Platform:
    def __init__(self, x, y, width, height, frictionCoefficient = .5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.frictionCoefficient = frictionCoefficient

        self.points = [[x, y], [x + width, y], [x + width, y + height], [x, y + height]]

        self.forceAttachments = [] # all of the forces attached to this platform

        platforms.append(self)

    def addNorm(self, box):
        return Force(-box.getNorm(), "n", 0)

class Incline(Platform):
    def __init__(self, x, y, width, angle):

        self.angle = angle
        
        height = abs(width) / math.tan(math.radians(angle)) # finds the height of our triangle

        Platform.__init__(x, y, width, height)

        self.points = [[x, y], [x + width, y], [x + width, y + height]]

    def addNorm(self, box):
        # this add norm is a bit different since the box would be sitting on it at an angle

        return Force(box.getNorm(), "n", self.angle + 180)
    

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
            xForce = self.magnitude * math.sin(math.radians(self.dir))
            yForce = self.magnitude * math.cos(math.radians(self.dir))
        
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

# "applied force"
class Thrusters(ForceObject):
    def __init__(self, magnitude, dir):
        ForceObject.__init__(magnitude, "a", dir)