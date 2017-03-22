#!/usr/local/bin/python

from random import randint

class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fog = []

class Map:
    def __init__(self, X, Y):
        self.__x = X
        self.__y = Y
        self.fog = []

        self.data = [[ '#' for _ in range(X) ]]
        for _ in range(Y-2):
            d = ['#']
            d.extend(' ' for _ in range(X-2))
            d.append('#')
            self.data.append(d)
        self.data.append([ '#' for _ in range(X) ])

        self.mineral = []
        for n in range(1,10):
            self.add_mineral(n)

        c = 0,0
        while self[c] != ' ':
            c = randint(1, self.__x - 2), randint(1, self.__y - 2)
        self[c] = '_'
        self.landing_zone = c

        self.acid = []
        for _ in range(X * Y // 15):
            c = 0,0
            while self[c] != ' ':
                c = randint(1, self.__x - 2), randint(1, self.__y - 2)
            self[c] = '~'
            self.acid.append(c)

        self.fog = [[ '#' for _ in range(X) ]]
        for _ in range(Y-2):
            d = ['#']
            d.extend('.' for _ in range(X-2))
            d.append('#')
            self.fog.append(d)
        self.fog.append([ '#' for _ in range(X) ])
        c = 0,0
        while self[c] != ' ':
            c = randint(1, self.__x - 2), randint(1, self.__y - 2)

        self.zerg = []

    def summary(self):
        return sum(m.amt for m in self.mineral) / (self.__x * self.__y)

    def __str__(self):
        return '\n'.join(' '.join(row) for row in reversed(self.fog))

    def __getitem__(self, key):
        if self.fog: 
            self.fog[key[1]][key[0]] = self.data[key[1]][key[0]]
        return self.data[key[1]][key[0]]

    def __setitem__(self, key, val):
        if self.fog:
           self.fog[key[1]][key[0]] = val
        self.data[key[1]][key[0]] = val

    def what_is_at(self, key):
        for z in self.zerg:
            if z.location == key:
                return 'Z'
        return self[key]

    def add_mineral(self, amt):
        c = 0,0
        while self[c] != ' ':
            c = randint(1, self.__x - 2), randint(1, self.__y - 2)

        l = Location(c[0], c[1])
        ctx = MineralContext(l, amt)
        self[l.x,l.y] = '*'
        self.mineral.append(ctx)

    def remove_zerg(self, z_id):
        for z in self.zerg:
            if z_id == id(z.zerg) and (z.location.x,z.location.y) == self.landing_zone:
                self[z.location.x, z.location.y] = '_'
                self.zerg.remove(z)
                return z.mineral, z.hp
        return None, None

    def add_zerg(self, z, health):
        c = self.landing_zone
        if self[c] != '_':
            return False

        l = Location(c[0], c[1])
        self.update_location_adjacent(l)

        ctx = DroneContext(l, z, health)
        self[l.x,l.y] = 'Z'
        self.zerg.append(ctx)

        return True

    def update_location_adjacent(self, l):
        l.north = self[l.x, l.y+1]
        l.south = self[l.x, l.y-1]
        l.east = self[l.x+1, l.y]
        l.west = self[l.x-1, l.y]
        return l

    def find_mineralcontext_at(self, pos):
        for z in self.mineral:
            if z.location.x == pos[0] and z.location.y == pos[1]:
                return z

        return None

    def find_zergcontext_at(self, pos):
        for z in self.zerg:
            if z.location.x == pos[0] and z.location.y == pos[1]:
                return z

        return None

    def move_to(self, l, d):
        if d == 'NORTH':
            new_l = (l.x, l.y + 1)
        elif d == 'SOUTH':
            new_l = (l.x, l.y - 1)
        elif d == 'EAST':
            new_l = (l.x + 1, l.y)
        elif d == 'WEST':
            new_l = (l.x - 1, l.y)
        else:
            new_l = (l.x, l.y)


        if new_l == (l.x, l.y):
            pass
        elif self[new_l] in ' _~':
            self[l.x, l.y] = ' '
            self.update_tile(l.x, l.y)
            l.x, l.y = new_l[0], new_l[1]
            self[new_l] = 'Z'
            self.update_location_adjacent(l)
        elif self[new_l] == 'Z':
            other = self.find_zergcontext_at(new_l)
            other.hp -= 7
        elif self[new_l] == '#':
            z = self.find_zergcontext_at( (l.x, l.y) )
            z.hp -= 1
        elif self[new_l] == '*':
            m = self.find_mineralcontext_at( new_l )
            if m.amt > 0:
                z = self.find_zergcontext_at( (l.x, l.y) )
                z.mineral += 1
                m.amt -= 1
                if m.amt <= 0:
                    self[m.location.x, m.location.y] = ' '
                    self.update_tile(m.location.x, m.location.y)
                    self.mineral.remove(m)
        else:
            raise Exception('UNKNOWN TERRAIN')

    def update_tile(self, x, y):
        if (x,y) == self.landing_zone:
            self[ x,y ] = '_'
        elif (x,y) in self.acid:
            self[ x,y ] = '~'


    def tick(self):
        # TODO: This might be unecessary now that the minerals
        # are removed upon mining.
        for m in self.mineral:
            if m.amt <= 0:
                self[m.location.x, m.location.y] = ' '
                self.update_tile(m.location.x, m.location.y)
                self.mineral.remove(m)
        for z in self.zerg:
            if (z.location.x, z.location.y) in self.acid:
                z.hp -= 3
            if z.hp <= 0:
                self[z.location.x, z.location.y] = ' '
                self.update_tile(z.location.x, z.location.y)
                self.zerg.remove(z)
        for z in self.zerg:
            self.update_location_adjacent(z.location)
            pos = z.location.x, z.location.y

            d = z.zerg.move(z.location)
# Reset location position so that the zerg cannot track or abuse it
            z.location = Location(pos[0], pos[1])
            self.update_location_adjacent(z.location)
            self.move_to(z.location, d)

class MineralContext:
    def __init__(self, l, amt):
        self.location = l
        self.amt = amt

class DroneContext:
    def __init__(self, l, z, hp):
        self.location = l
        self.zerg = z
#TODO: This should be maintained independent of whichever map they are on
        self.hp = hp
        self.mineral = 0
