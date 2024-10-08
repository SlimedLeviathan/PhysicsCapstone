# this file contains all of the main classes

# all angles are in degrees, so they have to be converted to radians for the calculations

import math, numpy
import pygame as pg

# variables that affect what gets shown on the screen
showEnergies = False

# global variables
# normal for gravity, but can be changed in the program
gravity = 9.8 # this is also here since this file should be the farthest down import
airDens = 1.204

boxSize = 50

boxes = []

pg.font.init()

font = pg.font.Font(None, 16)

def displayText(window: pg.Surface, x, y, text):
    window.blit(font.render(text, True, [255, 255, 255]), [x, y])

def pointInLine(point, line):
    lineMin = min(line)
    lineMax = max(line)

    return point > lineMin and point < lineMax

def oneDLineColl(line1, line2): # lines are : [p1, p2]
    return pointInLine(line1[0], line2) or pointInLine(line1[1], line2) or pointInLine(line2[0], line1)

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

    frictionCoefficient = .3

    def __init__(self, x, y, mass = 50):
        self.x = x
        self.y = y

        self.rect = pg.rect.Rect(self.x, self.y, self.x + boxSize, self.y + boxSize)

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
    
    def getAirResistance(self, speed):
        airRes = .5 * airDens * (speed ** 2) * self.dragCoe * self.crossSection

        if (speed < 0):
            airRes *= -1

        return airRes

    def applyFriction(self, endForce):
        # basically, we take the speed and forces currently acting on an object in order to make an accurate amount of friction
        # we also make sure the box is touching a platform

        frictions = []

        for data in self.collidingPlatforms:
            # currently, dont worry aout ow much of the platform is touching the box

            if (data[1] == "up" or data[1] == "down"):

                # find the friction force of the object


                xFriction = self.getFriction(data[0].frictionCoefficient)

                if (self.speed[0] == 0): # static friction
                    if xFriction > endForce[0]:
                        xFriction = endForce[0] # if the static friction is above the endForce, then we make sure it doesnt actually move the box

                else:
                    if (xFriction > endForce[0] + self.speed[0] / 2): # ok, so i REALLY could not find out how much friction actually affects an object with speed, so we do this to compensate
                        xFriction = endForce[0] + self.speed[0] / 2

                if (xFriction != 0):

                    if (xFriction > 0):
                        frictions.append(Force(xFriction, "f", 90))
                    
                    if (xFriction < 0):
                        frictions.append(Force(xFriction, "f", 270))
                

            if (data[1] == "left" or data[1] == "right"):
                pass

        # if the box is not touching any platform, and therefore, freefalling (as long as the endForce has some value greater than 0)
        # we calculate the air resistance

        if (len(self.collidingPlatforms) == 0):
            frictions.append(Force(self.getAirResistance(self.speed[0]), "Fa", 270)) # Fa

            frictions.append(Force(self.getAirResistance(self.speed[1]), "Fa", 180))
        
        return frictions

    def applyForces(self):

        netForce = [0, 0]

        for force in self.forces:
            netForce = force.applyForce(netForce)

        # if the box is touching the ground, and there is a net force, we add the friction force
        # we also take intoaccount the fact that the object might be moving as well, and add that as a force in the friction calcuations
        endForce = [netForce[0], netForce[1]]

        endForce[0] += self.mass * self.speed[0]
        endForce[1] += self.mass * self.speed[1]

        frictions = self.applyFriction(endForce)

        for force in frictions:
            netForce = force.applyForce(netForce)

        self.forces.extend(frictions)

        # we divide by 1000 since the measurements are in m/s and we are doing this every millisecond, so we have to change it a bit
        self.speed[0] += (netForce[0] / (self.mass * 1000)) 
        self.speed[1] += (netForce[1] / (self.mass * 1000)) 

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

        self.rect = pg.rect.Rect(self.x, self.y, boxSize, boxSize)

    def collisionDetect(self):
        # checks all platforms to see which ones this box is touching, then apply the forces
        for platform in platforms:
            if (abs((platform.y) - (self.y + boxSize)) <= abs(self.speed[1] * 1.05) + 1 and oneDLineColl([platform.x, platform.x + platform.width], [self.x, self.x + boxSize])): # if the difference in Ys are less than 1 (so they are touching top to bottom)

                self.addForce(platform.addNorm(self))

                self.collidingPlatforms.append([platform, "down"])

                self.addForce(Force(self.mass * gravity * -((self.speed[1] ** 2) * .5 * 1000), "s")) # im just saying spring since it uses the pressure of the object to keep it from falling

            elif (abs((platform.y + platform.height) - (self.y)) <= abs(self.speed[1] * 1.5) + 1 and oneDLineColl([platform.x, platform.x + platform.width], [self.x, self.x + boxSize])): # if the difference in Ys are less than 1 (so they are touching top to bottom)

                # we dont add a norm, but correct the forces later to set the box at the endge of the platform later

                self.collidingPlatforms.append([platform, "up"])

                self.addForce(Force(self.mass * gravity * ((self.speed[1] ** 2) * 1000 * .5), "s")) # im just saying spring since it uses the pressure of the object to keep it from falling

        # so boxes collide with each other
        for box in boxes:
            if (abs((box.y) - (self.y + boxSize)) <= abs(self.speed[1] * 1.05) + 1 and oneDLineColl([box.x, box.x + boxSize], [self.x, self.x + boxSize])): # if the difference in Ys are less than 1 (so they are touching top to bottom)

                self.addForce(box.addNorm(self))

                self.collidingPlatforms.append([box, "down"])

                self.addForce(Force(self.mass * gravity * -((self.speed[1] ** 2) * .5 * 1000), "s")) # im just saying spring since it uses the pressure of the object to keep it from falling

            elif (abs((box.y + boxSize) - (self.y)) <= abs(self.speed[1] * 1.5) + 1 and oneDLineColl([box.x, box.x + boxSize], [self.x, self.x + boxSize])): # if the difference in Ys are less than 1 (so they are touching top to bottom)

                # we dont add a norm, but correct the forces later to set the box at the edge of the platform later

                self.collidingPlatforms.append([box, "up"])

                self.addForce(Force(self.mass * gravity * ((self.speed[1] ** 2) * 1000 * .5), "s")) # im just saying spring since it uses the pressure of the object to keep it from falling

    # so collision between blocks works better
    def addNorm(self, box):
        return Force(-box.getNorm(), "n", 0)

    def forceObjectApply(self):
        for forceObject in self.forceObjects:
            self.forces.append(forceObject.getForce())

    def move(self):
        # clear the forces here rather than at the end so that we can draw the forces
        self.forces.clear() # clears the forces, since each millisecond they all need to re-add themselves in order to be relevant
        self.collidingPlatforms.clear()

        self.addGravity() # gravity comes first
        
        self.collisionDetect() # then the norms

        self.forceObjectApply() # then the force objects

        self.applyForces() # then we apply the forces

        self.x = self.speed[0] + self.x
        self.y = self.speed[1] + self.y

        self.setPoints()

    def addForce(self, force):
        self.forces.append(force)

    def getKineticEnergy(self):
        return .5 * self.mass * (self.speed[0] + self.speed[1])
    
    def getPotentialEnergy(self):
        height = ground.y - (self.y + boxSize)

        return self.mass * gravity * height

    def drawForces(self, window: pg.Surface): # figured out this is how you tell the IDE and other programmers what a parameter should be, doesnt affect actual python tho

        dirLines = {} # saves all lines made to this dict, each key is a direction and the value is a list of all ofthe lines inside of that direction
        # a line is [[startExtra], [endPoint], name]

        for force in self.forces:
            # find out how far in each direction the line should go

            if abs(force.magnitude) < 10:
                continue

            endPos = force.applyForce([0, 0])

            endPos[0] /= 10
            endPos[1] /= 10

            prevLines = []

            dir = force.dir

            if (force.magnitude < 0):
                # flip the direction to be oppoisite

                dir = (dir + 180) % 360

            dictRes = dirLines.get(dir)

            if (dictRes != None):   
                prevLines.extend(dictRes)
            
            prevLines.append([[0, 0], endPos, force.char])

            lineNum = 1

            for line in prevLines:
                
                startExtra = line[0]                

                # for now, im not worrying about diagonals
                if (dir == 0 or dir == 180):
                    startExtra[0] = (boxSize / (len(prevLines) + 1)) * lineNum

                    if (dir == 0):
                        startExtra[1] = boxSize + 1

                    else:
                        startExtra[1] = -1

                elif (dir == 90 or dir == 270):
                    startExtra[1] = (boxSize / (len(prevLines) + 1)) * lineNum

                    if (dir == 90):
                        startExtra[0] = boxSize + 1

                    else:
                        startExtra[0] = -1

                lineNum += 1

            dirLines.update({dir : prevLines})

        # print(dirLines)

        for dir, lines in dirLines.items():

            for line in lines:
                startPos = [self.x + line[0][0], self.y + line[0][1]]

                endPos = line[1]

                endPos[0] += startPos[0]
                endPos[1] += startPos[1]

                pg.draw.line(window, [255,255,255], startPos, endPos, 5)

                # we also need to put the name of the force onto the screen
                displayText(window, endPos[0] + 5, endPos[1] + 5, line[2])

    def drawEnergies(self, window : pg.Surface):
        displayText(window, self.x + 2, self.y + 2, f"P: {round(self.getPotentialEnergy(), 2)}")

        displayText(window, self.x + 2, self.y + 22, f"K: {round(self.getKineticEnergy(), 2)}")

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
        # because platforms dont move, we dont add any forces to it

        return Force(-box.getNorm(), "n", 0)
    

def setGround(window : pg.Surface):
    global ground

    ground = Platform(-100, window.get_height() - 100, window.get_width() + 200, 100)

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
        xForce = self.magnitude * round(math.sin(math.radians(self.dir)), 6) # rounds to six digits
        yForce = self.magnitude * round(math.cos(math.radians(self.dir)), 6)

        netForce[0] += math.floor(xForce)
        netForce[1] += math.floor(yForce)

        return netForce # returns the netForces
    
    def __repr__(self):
        return f"{self.char}: Angle:{self.dir} Magnitude:{self.magnitude}"

class ForceObject:
    def __init__(self, magnitude, char, dir):
        self.force = Force(magnitude, char, dir)

        self.maxMagnitude = magnitude

    def getForce(self):
        return self.force

class String(ForceObject):
    def __init__(self, maxMagnitude, dir):
        ForceObject.__init__(self, maxMagnitude, "t", dir) # it uses tension force

class Spring(ForceObject):
    def __init__(self, maxMagnitude, dir):
        ForceObject.__init__(self, maxMagnitude, "s", dir)

# "applied force"
class Thrusters(ForceObject):
    def __init__(self, magnitude, dir):
        ForceObject.__init__(self, magnitude, "a", dir)