#!/usr/local/bin/python


from random import randint, choice
from collections import deque

class Drone:

    cardinal = ["NORTH", "EAST", "SOUTH", "WEST"]
    cardinalIndex = {"NORTH":0, "EAST":1, "SOUTH":2, "WEST":3}
    turnMath = {"right": 1, "left": 3, "aboutFace": 2}

    def __init__(self):
        self.stepCount = 0
        self.direction = "NONE"
        self.instructions = deque([(2,"NORTH"), (2, "EAST"), (5, "SOUTH"), (5, "WEST"),
                    (7, "NORTH"),(7, "EAST"), (10, "SOUTH"), (10, "WEST"), (13, "NORTH"),
                    (13, "EAST"), (15, "SOUTH"), (15, "WEST"), (18, "NORTH"), (18, "EAST"),
                    (2, "SOUTH"), (2, "WEST"), (5, "NORTH")])
        self.returnPath = deque([])
        self.currStep = 0
        self.nBor = 0 
        self.sBor = 0
        self.eBor = 0
        self.wBor = 0
        self.dropX = -1
        self.dropY = -1
        self.headBack = False
        self.mined = 0
        self.home = 0
        self.beam = 0
        self.borderPatrol = False
        self.getInstructions()
        self.startSearch = "NONE"
        self.rightTurns = 0
        self.leftTurns = 0
        self.plane = 0
        self.barrier = 0
        self.current = "NONE"
        self.detour = False

    """ pops the new instructions from the deque """
    def getInstructions(self):
        if self.headBack == True:
            self.stepCount, self.direction = self.returnPath.popleft()
            print("RETURN COORDINATES", self.stepCount, self.direction)
        else:
            self.stepCount, self.direction = self.instructions.popleft()    
    
    """ calculates the path for the drone to head go back to the landing zone """
    def returnInstructions(self, x, y):
        print("Return Instructions")
        sideways = self.dropX - x
        upDown = self.dropY - y
        print("X{},Y{}".format(sideways, upDown))
        if sideways > 0:
            self.returnPath.appendleft((sideways, "EAST"))
        elif sideways < 0:
            sideways *= -1
            self.returnPath.appendleft((sideways, "WEST"))
        if upDown > 0:
            self.returnPath.appendleft((upDown, "NORTH"))
        elif upDown < 0:
            upDown *= -1 
            self.returnPath.appendleft((upDown, "SOUTH"))
        self.headBack = True
        self.getInstructions()

    """ This is the 'detour' method """ 
    def makeTurn(self, context, direction):
        indx = Drone.cardinalIndex[self.direction]
        index = Drone.turnMath[direction]
        print("MAKE TURN FACING:", self.direction, Drone.cardinal[(indx + index)%4])
        return Drone.cardinal[(indx + index)%4]
        
    """ this checks every direction for mines """
    def mineCheck(self, context):

        for items in Drone.cardinalIndex:
            if getattr(context,items.lower()) == "*":
                self.mined += 1
                return items
        return "NONE"


    def rightTurn(self, context):
        right = self.makeTurn(context, "right")
        self.rightTurns += 1
        if getattr(context, right.lower()) in "#~Z":
            right = self.makeTurn(context, "aboutFace")
            self.rightTurns += 1
        return right

    def leftTurn(self, context):
        left = self.makeTurn(context, "left")
        if getattr(context,left.lower()) not in "#~Z":
            self.leftTurns += 1
            return left
        return "NONE"

    def setStart(self, context):
        if self.startSearch == "NONE":
            if context.x | context.y == 1:
                self.startSearch = context.x, context.y


    """ LEFT OFF: You were planning on using the x and y coordinates to """
    """ determine if you have gone around an obstacle or around the whole """
    """ map, this is being done in the left turn portion of the this func """
    """ your adding them to a deque from the left. You will compare the """
    """ context.x and y with the zeroth element. If they are equal, you """
    """ have gone around the entire map, if x is larger or less than """
    """ (depending on the direction you are moving, then you will have """
    """ gone around an obstacle, and will want to prevent going in loops, or """
    """ potentially back to the beginning. """ 

    def perimeterSearch(self, context):
        if self.leftTurns and self.rightTurns == 0:
            if getattr(context, self.direction.lower()) in "#~Z":
                right = self.rightTurn(context)
                return right
            else:
                return self.direction

        elif self.rightTurns >= self.leftTurns:
            if getattr(context, self.direction.lower()) in "#~Z":
                left = self.leftTurn(context)
                if left != "NONE":
                    self.direction = left
                    return self.direction
                else:
                    self.direction = self.rightTurn(context)
                    return self.direction
            else:
                left = self.leftTurn(context)
                if left != "NONE":
                    self.direction = left
                    return self.direction
                return self.direction

        elif self.leftTurns > self.rightTurns:
            self.direction = self.rightTurn(context)
            return self.direction



    def move(self, context):
        
        mine = self.mineCheck(context)
        if mine != "NONE":
            return mine

        """ set the drop location """
        if self.dropX and self.dropY == -1:
            self.dropX = context.x
            self.dropY = context.y
            if self.dropX > self.dropY:
                self.direction = "SOUTH"
            else:
                self.direction = "WEST"
            self.borderPatrol = True
            #Debug statement
            print(self.dropX, self.dropY)

        if self.borderPatrol == True:
            if self.startSearch == "NONE":
                if getattr(context, self.direction.lower()) == "#":
                    self.setStart(context)
                return self.perimeterSearch(context)
            elif (context.x, context.y) == self.startSearch and self.rightTurns >= 4:
                print("Start Found")
                self.leftTurns = self.rightTurns = 0
                self.getInstructions()
                self.borderPatrol = False
                return self.rightTurn(context)
            else:
                return self.perimeterSearch(context)


        """ if headBack is set, return to the landing zone """
        if self.headBack == True:
            if context.x == self.dropX and context.y == self.dropY:
                print("AT LANDING ZONE")
                self.beam = 1
                return "CENTER"
            else:
                self.home = 0
                self.returnInstructions(context.x, context.y)
                #Debug Statement
                print("NOT AT LANDING YET", self.stepCount, self.direction)
            self.stepCount -= 1
            return self.direction

        """ check to see if they collected a certain number of minerals """
        if self.mined >= 15:
            #Debug Statement
            print("MINE CAPACITY")
            if context.x == self.dropX and context.y == self.dropY:
                self.beam = 1
                self.headBack = True
                return "CENTER"
            self.returnInstructions(context.x, context.y)
            self.stepCount -= 1
            return self.direction

        if self.detour == True:
            self.direction = self.perimeterSearch(context)
        
        """ while return is not set continue searching """ 
        if self.headBack == False and self.detour == False:
            if getattr(context,self.direction.lower()) in "#~Z":
                self.detour = True
                self.direction = self.perimeterSearch(context)
            if self.stepCount == 0:
                self.getInstructions()

        

        self.stepCount -= 1
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
            if self.zerg[self.downRange[a]].beam == 1:
                x = self.downRange.pop(a)
                self.returned.append(x)
                return 'RETURN {}'.format(x)
            a += 1
         #debug Statement
         print("returned", self.returned)
         return "NONE YET"
         
        
            


     


