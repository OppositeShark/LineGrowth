# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 16:47:50 2022

@author: degog
"""

import LineGrowth as LG
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
'''
Format (in order), S, L, R, X, P, O
'''
growthAlg = "m8S_Rn_XRn-n(0,0,0)t100"

#Interpreting Algorithm
LG.interpAlg(growthAlg.replace("n","1"))

mode = LG.stats.mode
#File Path Stuff
name = "BruteForce"+str(mode)
subname = re.match('m[0-9]*(.*)',growthAlg).groups()[0]
if not os.path.isdir(os.path.abspath(name)):
    # Directory
    directory = name
    # Parent Directory path
    parent_dir = os.path.abspath("")
    # Path
    path = os.path.join(parent_dir, directory)
    # Create the directory
    os.mkdir(path)
subPath = os.path.join(os.path.abspath(name),subname)
if not os.path.isdir(subPath):
    os.mkdir(subPath)

LG.stats.printstuff = False
LG.stats.writevideo = False

d = growthAlg.count('n')

def nd_range(d,n):
    if not d:
        yield ()
        return
    for outer in nd_range(d - 1, n):
        for inner in range(n):
            yield outer + (inner,)

for p in nd_range(d,mode):
    filename = growthAlg
    for i in range(d):
        filename = filename.replace('n',str(p[i]),1)
    print("----",filename,"----")
    LG.interpAlg(filename)
    LG.main(path = subPath+"\\"+filename)
