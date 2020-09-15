#!/usr/bin/python

import sys
import curses

class vvvmap:
    gatetiles = "0123456789"
    solids = "[]" + gatetiles

    def __init__(self, maplines):
        self.maplines = maplines
        self.init()
        self.verify()

    @classmethod
    def load(cls, files):
        maps = []
        lines = []
        for filename in files:
            ordinal = 1
            with open(filename, 'r') as file:
                for line in ([x for x in file] + ['--']):
                    line = line.rstrip("\n")
                    if line == '--':
                        if lines:
                            thismap = cls(lines)
                            thismap.filename = filename
                            thismap.ordinal = ordinal
                            ordinal += 1
                            maps.append(thismap)
                        lines = []
                    else:
                        lines.append(line)
        return maps

    def init(self):
        self.maptiles = []
        self.gatepos = [[] for i in range(10)]
        self.displaypos = None

        self.pos = [0,0]
        self.vel = [0,1,1]

        xc,yc = 0,0
        for line in self.maplines:
            self.maptiles.append([])
            quote = False
            for char in line:
                if char in 'AV' and not quote:
                    self.pos = [xc,yc]
                    if char == 'V':
                        vel = [0,-1,-1]
                    char = 's'
                elif char == 'D' and not quote:
                    self.displaypos = (xc,yc)
                    char = ' '
                elif char in self.gatetiles and not quote:
                    self.gatepos[int(char)].append((xc,yc))
                elif char == '"':
                    quote = not quote
                    char = ' '

                self.maptiles[yc].append(char)

                xc += 1
            xc = 0
            yc += 1

        self.maxyx = (len(self.maptiles)-1, max(len(row) for row in self.maptiles)-1)

        self.save = self.pos
        self.keys = 0
        self.timer = 0
        self.deaths = 0

    def verify(self):
        pass

    def drawmap(self,w):
        curses.cbreak()
        w.timeout(0)
        w.clear()

        for y in range(len(self.maptiles)):
            for x in range(len(self.maptiles[y])):
                w.addstr(y,x,self.maptiles[y][x],1)

    def start(self,w):
        while True:
            self.init()
            self.drawmap(w)
            if self.run(w):
                break

    def run(self,w):
        while (True):

            keylist = []
            while True:
                key = w.getch()
                if key == -1: break
                else: keylist.append(key)

            w.addstr(self.pos[1],self.pos[0],self.maptiles[self.pos[1]][self.pos[0]],1)

            for key in keylist:
                if key == ord('q'):
                    sys.exit()
                if key == ord('r'):
                    return False
                if key == ord('s'):
                    self.timer = 999
                    return True

                # control scheme A -- left/right sets horizontal motion, up/down stops it
                if True:
                    if key == curses.KEY_UP:
                        self.vel[0] = 0
                        self.vel[2] = -1
                    if key == curses.KEY_DOWN:
                        self.vel[0] = 0
                        self.vel[2] = 1
                    if key == curses.KEY_LEFT:
                        self.vel[0] = -1
                    if key == curses.KEY_RIGHT:
                        self.vel[0] = 1

                # control scheme B -- left/right changes horizontal motion incrementally
                else:
                    if key == curses.KEY_UP:
                        self.vel[2] = -1
                    if key == curses.KEY_DOWN:
                        self.vel[2] = 1
                    if key == curses.KEY_LEFT:
                        if self.vel[0] > -1:
                            self.vel[0] += -1
                    if key == curses.KEY_RIGHT:
                        if self.vel[0] < 1:
                            self.vel[0] += 1

            dead = False
            victory = False

            for dimension in (1,0):
                if self.vel[dimension] != 0:
                    newpos = list(self.pos)
                    newpos[dimension] += self.vel[dimension]
                    newcell = self.maptiles[newpos[1]][newpos[0]]

                    if newcell in self.solids:
                        newpos = self.pos
                        if dimension == 1:
                            self.vel[1] = self.vel[2]
                    if ((newcell == '=' and dimension == 1) or
                        (newcell == '|' and self.maptiles[self.pos[1]][self.pos[0]] == '|' and dimension == 0)):
                        self.vel[1] = -self.vel[1]
                        self.vel[2] = self.vel[1]
                
                    if newcell == 's':
                        w.addstr(self.save[1],self.save[0],'s',1)
                        self.save = newpos

                    if newcell == '$':
                        self.maptiles[newpos[1]][newpos[0]] = ' '
                        w.addstr(newpos[1],newpos[0],' ',1)
                        self.keys += 1
                        for gate in self.gatepos[self.keys % 10]:
                            self.maptiles[gate[1]][gate[0]] = ' '
                            w.addstr(gate[1],gate[0],' ',1)

                    if newcell == 'X':
                        dead = True
                        break
                    if newcell == 'E':
                        victory = True
                        break
                    self.pos = newpos

            if self.displaypos:
                displaystr = "$ = {0}; t = {1}; X = {2}".format(self.keys, self.timer, self.deaths)
                w.addstr(self.displaypos[1],self.displaypos[0],displaystr)

            w.addstr(self.save[1],self.save[0],'S',1)        
            w.addstr(self.pos[1],self.pos[0],'-AV'[self.vel[1]],1)        
            w.move(len(self.maptiles)-1,len(self.maptiles[-1]))
            w.refresh()

            bugles = 0
            if dead: bugles = 1
            if victory: bugles = 3
            for i in range(bugles):
                curses.beep()
                curses.flash()
                curses.napms(250)
        
            if dead:
                self.deaths += 1
                w.addstr(self.pos[1],self.pos[0],self.maptiles[self.pos[1]][self.pos[0]],1)
                self.pos = self.save
                updown = 1
                for check in (-1,1):
                    if self.maptiles[self.pos[1]+check][self.pos[0]] in '[]':
                        updown = check
                self.vel = [0,updown,updown]

            if victory:
                while True:
                    key = w.getch()
                    if key == ord('q'):
                        sys.exit()
                    if key == ord('r'):
                        return False
                    if key in map(ord," n\n"):
                        return True
                    curses.napms(100)

            self.timer += 0.1
            curses.napms(100)

def checksize(w,maxyx):
    winmaxyx = w.getmaxyx()
    return not (winmaxyx[0] < maxyx[0] or winmaxyx[1] < maxyx[1])

maplist = vvvmap.load(sys.argv[1:])
if not maplist:
    print "Usage: vvvert1g0.py <mapfile> [<mapfile> ...]"
    sys.exit(1)

maxmaxyx = (max([m.maxyx[0] for m in maplist]),max([m.maxyx[1] for m in maplist]))
if not curses.wrapper(lambda w: checksize(w, maxmaxyx)):
    print "To draw all these maps your window must be at least {0} by {1}.".format(*[d+1 for d in maxmaxyx])
    print "Please resize your window and try again."
    sys.exit(1)

for m in maplist:
    curses.wrapper(m.start)

for m in maplist:
    print "{3} {4}: $ = {0}; t = {1}; X = {2}".format(m.keys, m.timer, m.deaths, m.filename, m.ordinal)

if (len(maplist) > 1):
    sumkeys = sum([m.keys for m in maplist])
    sumtimer = sum([m.timer for m in maplist])
    sumdeaths = sum([m.deaths for m in maplist])
    print "{3}: $ = {0}; t = {1}; X = {2}".format(sumkeys, sumtimer, sumdeaths, "TOTAL")
