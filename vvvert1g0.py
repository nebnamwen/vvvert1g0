#!/usr/bin/python

import sys
import curses
from collections import namedtuple

class vvvmap:
    walltiles = "[]"
    gatetiles = "0123456789"
    solids = walltiles + gatetiles
    portaltiles = "abc"

    def __init__(self, maplines):
        self.maplines = maplines
        self.init()

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
        self.nocolor = []
        self.gatepos = [[] for i in range(10)]

        self.portals = {}
        for char in self.portaltiles:
            self.portals[char] = []

        self.displaypos = None

        self.colors = {}

        self.pos = [0,0]
        self.vel = [0,1,1]

        xc,yc = 0,0
        for line in self.maplines:
            self.maptiles.append([])
            self.nocolor.append([])

            quote = False
            nocolor = False

            for char in line:
                if char in 'AV' and not quote:
                    self.pos = [xc,yc]
                    if char == 'V':
                        self.vel = [0,-1,-1]
                    char = 's'
                elif char == 'D' and not quote:
                    self.displaypos = (xc,yc)
                    char = ' '
                elif char in self.gatetiles and not quote:
                    self.gatepos[int(char)].append((xc,yc))

                elif char in self.portaltiles and not quote:
                    existing = False
                    for portal in self.portals[char]:
                        if yc == portal.pos[1] and xc == portal.pos[0]+portal.size[0]:
                            portal.size[0] += 1
                            existing = True
                        elif xc == portal.pos[0] and yc == portal.pos[1]+portal.size[1]:
                            portal.size[1] += 1
                            existing = True
                        elif yc == portal.pos[1]+portal.size[1]-1 and xc < portal.pos[0]+portal.size[0]:
                            existing = True
                    if not existing:
                        p = namedtuple("portal", ["pos", "size"])([xc,yc],[1,1])
                        self.portals[char].append(p)

                elif char == '"':
                    quote = not quote
                    nocolor = quote
                    char = ' '

                elif char == '_' and quote:
                    nocolor = not nocolor
                    char = ' '
                elif char == '`' and quote:
                    nocolor = not nocolor
                    char = "'"
                elif char == '{' and quote:
                    nocolor = not nocolor
                    char = '('
                elif char == '}' and quote:
                    nocolor = not nocolor
                    char = ')'

                self.maptiles[yc].append(char)
                self.nocolor[yc].append(nocolor)

                xc += 1
            xc = 0
            yc += 1

        self.maxyx = (len(self.maptiles)-1, max(len(row) for row in self.maptiles)-1)

        self.save = self.pos
        self.keys = 0
        self.timer = 0.0
        self.deaths = 0

    def validate(self):
        return True

    def drawmap(self,w):
        curses.cbreak()
        w.timeout(0)
        w.clear()

        for y in range(len(self.maptiles)):
            for x in range(len(self.maptiles[y])):
                self.drawtile(w,(x,y))

    def drawtile(self,w,pos,char=None):
        x, y = pos
        if char is None: char = self.maptiles[y][x]
        if char in self.colors and (x >= len(self.nocolor[y]) or not self.nocolor[y][x]):
            w.addstr(y,x,char,self.colors[char])
        else:
            w.addstr(y,x,char)

    def init_colors(self):
        if curses.has_colors():
            curses.init_pair(1,curses.COLOR_CYAN,curses.COLOR_BLACK)
            for char in 'AV':
                self.colors[char] = curses.color_pair(1) | curses.A_BOLD

            curses.init_pair(2,curses.COLOR_BLACK,curses.COLOR_WHITE)
            for char in self.walltiles:
                self.colors[char] = curses.color_pair(2)

            curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK)
            self.colors['X'] = curses.color_pair(3) | curses.A_BOLD

            curses.init_pair(4,curses.COLOR_YELLOW,curses.COLOR_BLACK)
            self.colors['$'] = curses.color_pair(4) | curses.A_BOLD

            curses.init_pair(5,curses.COLOR_BLACK,curses.COLOR_YELLOW)
            for char in self.gatetiles:
                self.colors[char] = curses.color_pair(5)

            curses.init_pair(6,curses.COLOR_WHITE,curses.COLOR_CYAN)
            self.colors['E'] = curses.color_pair(6) | curses.A_BOLD

            for char in 'sS=|':
                self.colors[char] = curses.A_BOLD

            curses.init_pair(7,curses.COLOR_BLACK,curses.COLOR_MAGENTA)
            self.colors['a'] = curses.color_pair(7)

            curses.init_pair(8,curses.COLOR_BLACK,curses.COLOR_BLUE)
            self.colors['b'] = curses.color_pair(8)

            curses.init_pair(9,curses.COLOR_BLACK,curses.COLOR_GREEN)
            self.colors['c'] = curses.color_pair(9)

    def start(self,w):
        while True:
            self.init()
            self.init_colors()
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

            self.drawtile(w,self.pos)

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

                    while newcell in self.portaltiles:
                        numportals = len(self.portals[newcell])
                        for i in range(numportals):
                            p = self.portals[newcell][i]
                            if (newpos[0] >= p.pos[0] and newpos[0] < p.pos[0]+p.size[0]
                                and newpos[1] >= p.pos[1] and newpos[1] < p.pos[1]+p.size[1]):

                                outp = self.portals[newcell][numportals - i - 1]
                                for d in (0,1):
                                    newpos[d] += outp.pos[d] - p.pos[d]
                                newpos[dimension] += p.size[dimension] * self.vel[dimension]

                                newcell = self.maptiles[newpos[1]][newpos[0]]

                                break

                    if newcell in self.solids:
                        newpos = self.pos
                        if dimension == 1:
                            self.vel[1] = self.vel[2]

                    if ((newcell == '=' and dimension == 1) or
                        (newcell == '|' and self.maptiles[self.pos[1]][self.pos[0]] == '|' and dimension == 0)):
                        self.vel[1] = -self.vel[1]
                        self.vel[2] = self.vel[1]
                
                    if newcell == 's':
                        self.drawtile(w,self.save)
                        self.save = newpos

                    if newcell == '$':
                        self.maptiles[newpos[1]][newpos[0]] = ' '
                        self.drawtile(w,newpos)
                        self.keys += 1
                        for gate in self.gatepos[self.keys % 10]:
                            self.maptiles[gate[1]][gate[0]] = ' '
                            self.drawtile(w,gate)

                    if newcell == 'X':
                        dead = True
                        break
                    if newcell == 'E':
                        victory = True
                        break
                    self.pos = newpos

            if self.displaypos:
                displaystr = "$ = {0}; t = {1:.1f}; X = {2}".format(self.keys, self.timer, self.deaths)
                self.drawtile(w,self.displaypos,displaystr)
                for char in '$X':
                    if displaystr.find(char) >= 0:
                        self.drawtile(w,(self.displaypos[0]+displaystr.find(char),self.displaypos[1]),char)

            self.drawtile(w,self.save,'S')
            self.drawtile(w,self.pos,'-AV'[self.vel[1]])
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
                w.addstr(self.pos[1],self.pos[0],self.maptiles[self.pos[1]][self.pos[0]])
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

def main():
    maplist = vvvmap.load(sys.argv[1:])
    if not maplist:
        print("Usage: vvvert1g0.py <mapfile> [<mapfile> ...]")
        sys.exit(1)

    problems = False
    for m in maplist:
        if not m.validate():
            problems = True
    if problems:
        sys.exit(1)

    winsize = curses.wrapper(lambda w: w.getmaxyx())
    if winsize[0] < 24 or winsize[1] < 80:
        print("vvvert1g0 is designed to run in an 80x24 terminal window.")
        print("Please resize your window and try again.")
        sys.exit(1)

    for m in maplist:
        curses.wrapper(m.start)

    for m in maplist:
        print("{3} {4}: $ = {0}; t = {1:.1f}; X = {2}".format(m.keys, m.timer, m.deaths, m.filename, m.ordinal))

    if (len(maplist) > 1):
        sumkeys = sum([m.keys for m in maplist])
        sumtimer = sum([m.timer for m in maplist])
        sumdeaths = sum([m.deaths for m in maplist])
        print("{3}: $ = {0}; t = {1:.1f}; X = {2}".format(sumkeys, sumtimer, sumdeaths, "TOTAL"))

if __name__ == "__main__":
    main()
