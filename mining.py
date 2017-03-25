#!/usr/local/bin/python


from random import randint, choice
from collections import deque
from time import sleep


class Drone:

    cardinal = ["NORTH", "EAST", "SOUTH", "WEST"]
    cardinalIndex = {"NORTH": 0, "EAST": 1, "SOUTH": 2, "WEST": 3}
    turnMath = {"right": 1, "left": 3, "aboutFace": 2}

    def __init__(self):
        self.stepCount = 0
        self.direction = "NONE"
        self.returnPath = deque([])
        self.nBor = 0
        self.sBor = 1
        self.eBor = 0
        self.wBor = 1
        self.dropX = -1
        self.dropY = -1
        self.headBack = False
        self.mined = 0
        self.home = 0
        self.beam = 0
        self.borderPatrol = True
        self.startSearch = False
        self.rightTurns = 0
        self.leftTurns = 0
        self.current = "NONE"
        self.detour = False
        self.startX = 0
        self.startY = 0
        self.mapped = False
        self.tempDir = "NONE"

    def getInstructions(self, context):
        """ getInstructions will return the current instructions from a """
        """ deque """
        if self.detour is False:
            self.stepCount, self.direction = self.returnPath.popleft()
        if self.leftTurns == 0 and self.rightTurns == 0:
            if getattr(context, self.direction.lower()) == "*":
                self.rightTurns += 1
                self.direction = self.makeTurn(context, "right")
        if self.leftTurns < self.rightTurns:
            left = self.makeTurn(context, "left")
            if getattr(context, left.lower()) != "*":
                self.direction = self.makeTurn(context, "left")
                self.leftTurns = self.rightTurns = 0
                self.detour = False

    def returnInstructions(self, context):
        """ Return instructions will map back the path the Drone must take """
        """ to the landing zone """
        self.leftTurns = self.rightTurns = 0
        sideways = abs(self.dropX - context.x)
        upDown = abs(self.dropY - context.y)
        if self.dropX == context.x | self.dropY == context.y:
            if self.dropX == context.x:
                if self.dropY > context.y:
                    self.returnPath.appendleft((upDown, "NORTH"))
                elif self.dropY < context.y:
                    self.returnPath.appendleft((upDown, "SOUTH"))
            elif self.dropY == context.y:
                if self.dropX > context.x:
                    self.returnPath.appendleft((sideways, "EAST"))
                elif self.dropx < context.x:
                    self.returnPath.appendleft((sideways, "WEST"))
        else:
            if self.dropX > context.x:
                self.returnPath.appendleft((sideways, "EAST"))
            elif self.dropX < context.x:
                self.returnPath.appendleft((sideways, "WEST"))
            if self.dropY > context.y:
                self.returnPath.appendleft((upDown, "NORTH"))
            elif self.dropY < context.y:
                self.returnPath.appendleft((upDown, "SOUTH"))
        self.headBack = True
        self.getInstructions(context)

    def makeTurn(self, context, direction):
        """ makeTurn will return the direction that is either to the left """
        """ right, or to the back(aboutFace) of the drone """
        indx = Drone.cardinalIndex[self.direction]
        index = Drone.turnMath[direction]
        return Drone.cardinal[(indx + index) % 4]

    """ this checks every direction for mines """
    def mineCheck(self, context):
        """ mineCheck will check the Drone's immediate surroundings for """
        """ minerals, if their are minerals, they are mined immediately """
        for items in Drone.cardinal:
            if getattr(context, items.lower()) == "*":
                self.mined += 1
                return items
        return "NONE"

    def rightTurn(self, context):
        """ Left turn will move the drone right of it's current """
        """ direction, the method will also update the drone's right """
        """ counter """
        right = self.makeTurn(context, "right")
        self.rightTurns += 1
        if getattr(context, right.lower()) in "#~Z":
            right = self.makeTurn(context, "aboutFace")
            self.rightTurns += 1
        return right

    def leftTurn(self, context):
        """ Left turn will move the drone left of it's current """
        """ direction, the method will also update the drone's left counter """
        left = self.makeTurn(context, "left")
        if getattr(context, left.lower()) not in "#~Z":
            self.leftTurns += 1
            return left
        return "NONE"

    def setStart(self, context):
        """ This method sets the starting location for border searches """
        """ It obtains the x and y coordinates if the Drone encounters a """
        """ wall and the x and y == 1 """
        if getattr(context, self.direction.lower()) == "#":
            if context.x == 1 or context.y == 1:
                self.startX = context.x
                self.startY = context.y
                self.startSearch = True

    def navigate(self, context):
        """ Navigate will check the drone's path for obstacles, and will """
        """ keep track of the turns it has made to get back on track """
        if self.leftTurns == 0 and self.rightTurns == 0:
            if getattr(context, self.direction.lower()) in "#~Z":
                if self.borderPatrol is False:
                    self.detour is True
                if getattr(context, self.direction.lower()) == "Z":
                    self.zergImpact = True
                self.direction = self.rightTurn(context)

        elif self.rightTurns >= self.leftTurns:
            left = self.leftTurn(context)
            if left != "NONE":
                if self.borderPatrol is True:
                    self.direction = left
                else:
                    if self.direction == "NORTH":
                        if (context.x - self.wBor) > 0:
                            self.direction = left
                        else:
                            self.leftTurns -= 1
                    elif self.direction == "SOUTH":
                        if (self.eBor - context.x) > 0:
                            self.direction = left
                        else:
                            self.leftTurns -= 1
                    elif self.direction == "EAST":
                        if (self.nBor - context.y) > 0:
                            self.direction = left
                        else:
                            self.leftTurns -= 1
                    elif self.direction == "WEST":
                        if (context.y - self.sBor) > 0:
                            self.direction = left
                        else:
                            self.leftTurns -= 1

            elif getattr(context, self.direction.lower()) in "#~Z":
                if getattr(context, self.direction.lower()) == "Z":
                    self.zergImpact = True
                self.direction = self.rightTurn(context)

        elif self.leftTurns > self.rightTurns:
            if self.borderPatrol is True:
                self.direction = self.rightTurn(context)
                self.leftTurns = self.rightTurns = 0
                self.detour = False
            else:
                if self.direction == "NORTH":
                    if (self.nBor - context.y) == 0:
                        self.direction = self.rightTurn(context)
                        self.detour = False
                        self.leftTurns = 0
                        self.rightTurns = 0
                    else:
                        self.leftTurns = self.rightTurns

                elif self.direction == "SOUTH":
                    if (context.y - self.sBor) == 0:
                        self.direction = self.rightTurn(context)
                        self.detour = False
                        self.rightTurns = 0
                        self.leftTurns = 0
                    else:
                        self.leftTurns = self.rightTurns

                elif self.direction == "EAST":
                    if (self.eBor - context.x) == 0:
                        self.direction = self.rightTurn(context)
                        self.detour = False
                        self.rightTurns = 0
                        self.leftTurns = 0
                    else:
                        self.leftTurns = self.rightTurns

                elif self.direction == "WEST":
                    if (context.x - self.wBor) == 0:
                        self.direction = self.rightTurn(context)
                        self.detour = False
                        self.rightTurns = 0
                        self.leftTurns = 0
                    else:
                        self.leftTurns = self.rightTurns

    def move(self, context):

        if self.headBack is True:
            """ This section of the code will check to see if the Drone """
            """ has been called back by the overlord. If so, the Drone """
            """ will cease current methods and operations and return back """
            """ to the landing zone on as straight of a path as possible """
            if context.x == self.dropX and context.y == self.dropY:
                self.beam = 1
                return "CENTER"
            else:
                self.home = 0
                self.returnInstructions(context)
            self.stepCount -= 1
            return self.direction

        mine = self.mineCheck(context)
        if mine != "NONE":
            return mine

        """ set the drop location """
        if self.dropX == -1 and self.dropY == -1:
            self.dropX = context.x
            self.dropY = context.y
            if self.dropX > self.dropY:
                self.direction = "SOUTH"
            else:
                self.direction = "WEST"
            print(self.dropX, self.dropY)

        if self.borderPatrol is True:
            """ This section of the code controls the Drone's Border """
            """ search. This updates borders as they are discovered """
            """ sets the starting position, and identifies the drone """
            """ when it has arrived at it's starting point """
            if self.direction == "NORTH":
                if context.y > self.nBor:
                    self.nBor = context.y
            if self.direction == "EAST":
                if context.x > self.eBor:
                    self.eBor = context.x

            if self.startSearch is False:
                self.setStart(context)
                self.navigate(context)
                return self.direction

            if self.startSearch is True:
                xDistance = context.x - self.startX
                yDistance = context.y - self.startY
                if xDistance == 0 and yDistance == 0:
                    if self.rightTurns >= 4:
                        self.mapped = True
                        self.leftTurns = self.rightTurns = 0
                        self.borderPatrol = False
                        return self.direction

            self.navigate(context)
            return self.direction

        if self.headBack is False:
            """ This section of the code handles the inner loop of the """
            """ function. After the zergs have completed their border """
            """ search, and before they are called back by the Overlord """
            """ they will begin to spiral from the outside in. """
            """ as the Drone hits each previously discovered border """
            """ it will turn right, and then re-define the border """
            """ based off of it's current position """
            if self.detour is False:
                if self.direction == "NORTH":
                    if (self.nBor - context.y) < 3:
                        self.nBor = context.y
                        self.leftTurns = self.rightTurns = 0
                        self.direction = "EAST"
                elif self.direction == "SOUTH":
                    if (context.y - self.sBor) < 3:
                        self.sBor = context.y
                        self.leftTurns = self.rightTurns = 0
                        self.direction = "WEST"
                elif self.direction == "EAST":
                    if (self.eBor - context.x) < 3:
                        self.eBor = context.x
                        self.leftTurns = self.rightTurns = 0
                        self.direction = "SOUTH"
                elif self.direction == "WEST":
                    if (context.x - self.wBor) < 3:
                        self.wBor = context.x
                        self.leftTurns = self.rightTurns = 0
                        self.direction = "NORTH"
            self.navigate(context)
            return self.direction


class Overlord:
    def __init__(self, total_ticks):
        self.maps = {}
        self.zerg = {}
        self.deployed = {}
        self.droneRatio = 0
        self.downRange = []
        self.currDrone = -1
        self.numDeployed = 0
        self.returned = []
        self.ticksRemaining = total_ticks
        self.returnDistance = {}
        for _ in range(6):
            z = Drone()
            self.zerg[id(z)] = z
            self.downRange.append(id(z))

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary
        self.deployed[map_id] = []

    def farthestCorner(self, zerg):
        """ This function will take the borders of the map the drone's """
        """ identify, as well as their landing zones. The function """
        """ the distance from the corner furthest away from the LZ. """
        """ This is done to determine the longest possible path back """
        """ to the landing zone. When the number of ticks falls below """
        """ each drone's return distance, the Overlord calls them back """
        distanceList = []

        lz = zerg.dropX + zerg.dropY

        firstDistance = abs((zerg.nBor + zerg.eBor) - lz) + 5

        secondDistance = abs((zerg.wBor + zerg.nBor) - lz) + 5

        thirdDistance = abs((zerg.sBor + zerg.eBor) - lz) + 5

        fourthDistance = abs((zerg.sBor + zerg.wBor) - lz) + 5

        distanceList.append(firstDistance)

        distanceList.append(secondDistance)

        distanceList.append(thirdDistance)

        distanceList.append(fourthDistance)

        return max(distanceList)

    def action(self):
        self.ticksRemaining -= 1
        if self.numDeployed != 5:
            for mapped, deployed in self.deployed.items():
                if len(deployed) == 0:
                    self.currDrone += 1
                    self.numDeployed += 1
                    self.deployed[mapped].append(
                                                self.downRange[self.currDrone])
                    return 'DEPLOY {} {}'.format(
                                                self.downRange[self.currDrone],
                                                mapped)

        for mapped, deployed in self.deployed.items():
            for drone in deployed:
                if self.zerg[drone].mapped is False:
                    returnDis = self.farthestCorner(self.zerg[drone])
                    self.returnDistance[drone] = returnDis

        for drone, distance in self.returnDistance.items():
            if distance >= self.ticksRemaining:
                self.zerg[drone].headBack = True

        for mapped, deployed in self.deployed.items():
            for drone in deployed:
                if self.zerg[drone].beam == 1:
                    self.zerg[drone].beam = 0
                    return 'RETURN {}'.format(drone)
        return "NONE"
