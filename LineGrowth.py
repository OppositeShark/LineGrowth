# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 22:49:29 2022

@author: degog
"""

from PIL import Image
from PIL import ImageDraw
import random

import math
import itertools

import threading
import multiprocessing as mp

import time
import os
import re


"""
m = type/mode

O = by the power of (2**x)
P = to the power of (x**2)
X = multiplyby
R = turn right
L = turn left
S = stay
x = length
_ = different branch
- = differentiate between different commands

t = iterations

(x,y,a) = initial point
a = angle

EX:
m16XR2-3x2_S3(0,0,0)(0,1,2)t100

mode: 16
Branch 1: multiply by 2 then turn right 3 and extend by 2
Branch 2: Stay at 3
initial points: (0,0,0) and (0,1,2)
iterations:100
"""

def interpAlg(growthAlg):
    stats.name = growthAlg
    #Mode
    mode = re.search("m[0-9]*",growthAlg)
    if mode != None:
        stats.mode = int(mode.group().strip('m'))
        growthAlg = growthAlg[mode.end():]
    else:
        stats.mode = 8
    #Iterations
    mode = re.search("t[0-9]*",growthAlg)
    if mode != None:
        stats.iterations = int(mode.group().strip('t'))
        growthAlg = growthAlg[:mode.start()]
    else:
        stats.iterations = 100
    #Points
    points = re.findall("\(.*?\)",growthAlg)
    initpoints = set()
    maxX = 0
    maxY = 0
    for i in points:
        point = eval(i)
        initpoints.add(point)
        if abs(point[0])>maxX:
            maxX = abs(point[0])
        if abs(point[1])>maxY:
            maxY = abs(point[1])
    stats.maxStartX = maxX
    stats.maxStartY = maxY
    stats.initpoints = initpoints
    #Values/growth
    vals = growthAlg.split("(", 1)[0]
    vals = vals.split("_")
    growthvals = []
    maxExtend = 1
    for i in vals:
        commands = re.search('[A-Z]*',i)
        nums = i[commands.end():]
        nums = nums.split('-')
        if 'x' in nums[-1]:
            nums[-1],dist = nums[-1].split('x')
            dist = float(dist)
            if dist>maxExtend:
                maxExtend = dist
        else:
            dist = 1
        commands = list(commands.group())
        assert len(commands)==len(nums)
        command = "x"
        for i,n in zip(commands[::-1],nums[::-1]):
            if i == 'X':
                command = command.replace('x','('+'x*'+n+')')
            elif i == 'R':
                command = command.replace('x','('+'x+'+n+')')
            elif i == 'L':
                command = command.replace('x','('+'x-'+n+')')
            elif i == 'O':
                command = command.replace('x','('+n+'**x'+')')
            elif i == 'P':
                command = command.replace('x','('+'x**'+n+')')
            elif i == 'S':
                pass
            else:
                raise "Bad Growth Command"
        print(command)
        func = eval("lambda x:"+command)
        growthvals.append((func,dist))
    stats.maxExtend = maxExtend
    stats.growthvals = growthvals

'''
 - X +
   ^   -
  <o>  Y
   v   +

directions3
   1

0     2

directions 4?
 2
3 1
 0

directions8
6 5 4
7   3
0 1 2

directions6
 4  3
5    2
 0  1
 
directions16

4  5  6  7  8
3           9
2           10
1           11
0  15 14 13 12
'''

class vector():
    def __init__(self, x, y, d, dmode):
        self.x = x
        self.y = y
        self.d = d%dmode
        self.dmode = dmode
    
    directions3 = {
        0:(-3,1),
        1:(0,-3),
        2:(3,1)
    }
    
    directions4 = {
        0:(0,1),
        1:(1,0),
        2:(0,-1),
        3:(-1,0)
    }
    
    directions6 = {
        0:(-1,3),
        1:(1,3),
        2:(3,0),
        3:(1,-3),
        4:(-1,-3),
        5:(-3,0)
    }
    
    directions8 = {
        0:(-1,1),
        1:(0,1),
        2:(1,1),
        3:(1,0),
        4:(1,-1),
        5:(0,-1),
        6:(-1,-1),
        7:(-1,0)
    }
    
    directions16 = {
        0:(-2,2),
        1:(-2,1),
        2:(-2,0),
        3:(-2,-1),
        4:(-2,-2),
        5:(-1,-2),
        6:(0,-2),
        7:(1,-2),
        8:(2,-2),
        9:(2,-1),
        10:(2,0),
        11:(2,1),
        12:(2,2),
        13:(1,2),
        14:(0,2),
        15:(-1,2)
    }
    
    dmodes = {
        3:directions3,
        4:directions4,
        6:directions6,
        8:directions8,
        16:directions16
        }
    dlengths = {k:abs(max(itertools.chain.from_iterable(v.values()),key = abs)) for k,v in dmodes.items()}
    
    def extend(self, direction, dist = 1):
        dx, dy = vector.dmodes[self.dmode][direction%self.dmode]
        return ((self.x+(dist*dx)),(self.y+(dist*dy)))
    
    def turnRight(self):
        return (self.d+1)%self.dmode
    
    def turnLeft(self):
        return (self.d-1)%self.dmode
    
    def getPoint(self):
        return (self.x,self.y)
    
    def getDirection(self):
        return self.d
    
    def getMode(self):
        return self.dmode
    
    def get(self):
        return self.getPoint() + (self.getDirection(),)
    
    def __hash__(self):
        return hash((self.getPoint()))
    
    def __repr__(self):
        return str(self.get())
      
BLUE=(0,0,255)
RED=(255,0,0)
GREEN=(0,255,0)
YELLOW=(255,255,0)
WHITE=(255,255,255)
PINK=(255,0,255)
ORANGE=(255,100,0)
PURPLE=(85,26,139)
BLACK=(0,0,0)

rainbow = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

#%%File Stuff

class stats():
    name = ""
    mode = 4
    iterations = 100
    maxExtend = 2
    maxStartX = 0
    maxStartY = 0
    linelength = 1
    linewidth = 1
    shift = (0,0)
    img = None
    draw = None
    initpoints = set((0,0,0))
    growthvals = [(lambda x:x-1,1),(lambda x:x+1,1)]
    printstuff = True
    writevideo = False
    
def makeImg():
    stats.linelength = 4/vector.dlengths[stats.mode]
    stats.linewidth = 1
    stats.imgwidth = round((vector.dlengths[stats.mode]*2+0.5)*stats.iterations*stats.linelength*stats.maxExtend)
    stats.imgheight = stats.imgwidth
    
    stats.imgwidth+=2*stats.maxStartX
    stats.imgheight+=2*stats.maxStartY
    
    shiftX = round(stats.imgwidth/2)
    shiftY = round(stats.imgheight/2)
    stats.shift = (shiftX, shiftY)
    
    stats.img = Image.new('RGB',(stats.imgwidth,stats.imgheight),color = (0,0,0))
    stats.draw = ImageDraw.Draw(stats.img)

def drawLine(vector1, vector2, color = (255,255,255)):
    vp = vector1.getPoint()+ vector2.getPoint()
    xy = [round((stats.linelength*vp[i]) + stats.shift[i%2]) for i in range(4)]
    stats.draw.line(xy, color, stats.linewidth)

#%%Calculation

#Initial Points

#initpoints = [[random.randint(-10,10) for n in range(3)] for i in range(10)]
#initpoints = set([tuple(p) for p in initpoints])

def isUsed(xy, cutUsedPoints):
    return xy in cutUsedPoints

#Limit points in UsedPoints
def updateBox(points, cutUsedPoints, usedPoints):
    #A circle
    r = math.sqrt(min([p[0]**2+p[1]**2 for p in points]))-(vector.dlengths[stats.mode])
    r = r**2
    cutUsedPoints.clear()
    for xy in usedPoints:
        if (xy[0]**2+xy[1]**2)>=r:
            cutUsedPoints.add(xy)
    
#Function for making next point
def nextPoint(turn, d, v):
    return vector(*(v.extend(turn, d)+(turn,)+(v.getMode(),)))
    
def makeNextPoint(nextPoints, turn, v, d = 1):
    np = nextPoint(turn, d, v)
    if not isUsed(np.getPoint()):
        nextPoints.append(np.get())
    else:
        for onp in nextPoints:
            if onp[:2] == np.getPoint():
                nextPoints.remove(onp)
                break
    return np

def calcPoints(points, growthvals, newColor, usedPoints, cutUsedPoints):
    for point in points:
        p = vector(*(point+(stats.mode,)))
        d = p.getDirection()
        #Adds to host point looping through growth branches
        for newangle, distance in growthvals:
            np = makeNextPoint(newangle(d), p, distance)
            #Draw Lines to initial "branch"
            drawLine(p,np,newColor)
            usedPoints.add(p)
            cutUsedPoints.add(p)


def main(path = None, threads = 0):
    #Create Image
    makeImg()
    
    #Starting Values
    initpoints = stats.initpoints
    growthvals = stats.growthvals
    nextPoints = []
    #Set up initial points
    points = list(initpoints)
    usedPoints = {p[:2] for p in initpoints}
    
    cutUsedPoints = usedPoints.copy()
    
    removePoints = []
    nThreads = threads    
            
    #Start Timer
    tstart = time.time()
    
    #n is used for printing percent done
    n = stats.iterations/100
    #Color Change Constant
    colorchange = 255/stats.iterations
    for i in range(stats.iterations):
        #Print percent done
        if stats.printstuff:
            print((i/n),"%")
        
        #Color
        newColor = (round(255-(colorchange*i)),random.randint(0, 255),255)
        
        #Threading the calculation
        calcPoints(points, growthvals, newColor, usedPoints, cutUsedPoints)
        
        points = nextPoints.copy()
        #Resetting for next generation
        removePoints.clear()
        nextPoints.clear()
        updateBox()
    
    #%% Save File
    if not os.path.isdir(os.path.abspath("Saved_Images")):
        # Directory
        directory = "Saved_Images"
        # Parent Directory path
        parent_dir = os.path.abspath("")
        # Path
        path = os.path.join(parent_dir, directory)
        # Create the directory
        os.mkdir(path)
    if path == None:
        path = os.path.abspath("Saved_Images")+"\\"+stats.name
    path+=".png"
    if stats.writevideo:
        #WIP
        pass
    else:
        stats.img.save(path,"png")
    print("Time Taken: %s" %(time.time()-tstart))
    if stats.printstuff:
        stats.img.show()

def testMain():
    stats.printstuff = True
    stats.writevideo = False
    #At 500 seconds
    interpAlg("m16S_XR9-1(0,0,0)t400")
    main(threads = 1)

if __name__ == "__main__":
    stats.printstuff = True
    stats.writevideo = False
    testMain()