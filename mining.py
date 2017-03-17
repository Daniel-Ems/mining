#!/usr/local/bin/python


from random import randint, choice
from collections import deque

class Drone:
    

    def __init__(self):
        self.stepCount = 0
        self.direction = "NONE"
        self.instructions = deque([(2,"NORTH"), (2, "EAST"), (5, "SOUTH"), (5, "WEST"),
                    (7, "NORTH"),(7, "EAST"), (10, "SOUTH"), (10, "WEST"), (13, "NORTH"),
                    (13, "EAST"), (15, "SOUTH"), (15, "WEST"), (18, "NORTH"), (18, "EAST")])
        self.currStep = 0
        self.nBor = 0 
        self.sBor = 0
        self.eBor = 0
        self.wBor = 0
        self.dropX = -1
        self.dropY = -1
        self.beam = False
        self.mined = 0
        self.home = 0
        self.good = 0
    def getInstructions(self):

        return self.instructions.popleft()    
    
    def returnInstructions(self, x, y):
        sideways = self.dropX - x
        upDown = self.dropY - y
        if sideways > 0:
            self.instructions.appendleft((sideways, "EAST"))
        else:
            sideways *= -1
            self.instructions.appendleft((sideways, "WEST"))
        if upDown > 0:
            self.instructions.appendleft((upDown, "NORTH"))
        else:
            upDown *= -1 
            self.instructions.appendleft((upDown, "SOUTH"))
        self.beam = True
        self.stepCount, self.direction = self.getInstructions()
        
    def move(self, context):

        if self.mined >= 10 and self.beam == False:
            return self.returnInstructions(context.x, context.y)

        if self.beam == True:
            if self.stepCount == 0 and self.home == 0:
                self.home += 1
                self.stepCount, self.direction = self.getInstructions()
            if self.stepCount == 0 and self.home == 1:
                if context.x != self.dropX | context.y != self.dropY:
                    self.home = 0
                    self.returnInstructions(context.x, context.y)
                else:
                    self.good = 1
                    return "CENTER"
            self.stepCount -= 1
            return self.direction

        if self.dropX and self.dropY == -1:
            self.dropX = (context.x)
            self.dropY = (context.y)

        if self.stepCount == 0 and self.currStep != 5 and self.currStep != 13:
            self.stepCount, self.direction = self.getInstructions()
            self.currStep = self.stepCount
        elif self.stepCount == 0:
            self.currStep = 0
            if self.direction == "SOUTH":
                return "NORTH"
            elif self.direction == "EAST":
                return "WEST"
            elif self.direction == "WEST":
                return "EAST"
            else:
                return "SOUTH"
        if self.beam == False:
            if self.direction == 'NORTH':
                if context.north == '*':
                    self.mined += 1
                    return self.direction
                elif context.north == '#':
                    self.stepCount, self.direction = self.getInstructions()
                    self.stepCount -= 1
                    return "EAST"
                self.stepCount -= 1
                return self.direction
            elif self.direction == 'SOUTH':
                if context.south == '*':
                    self.mined += 1
                    return self.direction
                elif context.south == '#':
                    self.stepCount, self.direction = self.getInstructions()
                    self.stepCount -= 1
                    return "WEST"
                self.stepCount -= 1
                return self.direction
            elif self.direction == 'EAST':
                if context.east == '*':
                    self.mined += 1
                    return self.direction
                elif context.east == '#':
                    self.stepCount, self.direction = self.getInstructions()
                    self.stepCount -= 1
                    return "SOUTH"
                self.stepCount -= 1
                return self.direction
            else:
                if context.west == '*':
                    self.mined += 1
                    return self.direction
                elif context.west == '#':
                    self.stepCount, self.direction = self.getInstructions()
                    self.stepCount -= 1
                    return "NORTH"
                self.stepCount -= 1
                return self.direction
            if context.x | context.y < 3:
                stripSearch(context)


class Overlord:
    def __init__(self, total_ticks):
        self.maps = {}
        self.zerg = {}
        self.deployed = {}
        self.droneRatio = 0
        self.downRange = []
        self.currDrone = -1
        self.numDeployed = 0

        for _ in range(6):
            z = Drone()
            self.zerg[id(z)] = z
            self.downRange.append(id(z))

    def add_map(self, map_id, summary):
        self.maps[map_id] = summary
        self.deployed[map_id] = 0
        self.ratio()

    def ratio(self):
        self.droneRatio = 6/len(self.maps)

    def action(self):
         a = 0
         if self.numDeployed != 6:
            for mapped, deployed in self.deployed.items():
                if deployed < self.droneRatio:
                    self.deployed[mapped] += 1
                    self.currDrone+= 1
                    self.numDeployed += 1
                    return 'DEPLOY {} {}'.format(self.downRange[self.currDrone],
                                         mapped)
         while a <= len(self.downRange)-1:
            if self.zerg[self.downRange[a]].good == 1:
                x = self.downRange.pop(a)
                return 'RETURN {}'.format(x)
            print("Status of zerg", self.downRange[a], "Good =", self.zerg[self.downRange[a]].good)
            a += 1
         return "FUCK OFF"
         
        
            


     


