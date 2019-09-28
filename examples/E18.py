#!/usr/bin/env python

# python E18.py --dev=file:../images/rot4.mjpg

import cv2          as cv
import numpy        as np

from umucv.stream   import autoStream
from umucv.htrans   import htrans, Pose, kgen
from umucv.util     import lineType, cube
from umucv.contours import extractContours, redu

# Movimiento del muñeco
# Mas incremento mas velocidad
incrementoMov = 0.05

persona = np.array([ 
    [0.5,0.25,0],
    [0.5,0.25,0.5], 
    [1,0.25,0],
    [0.5,0.25,0.5], 

    [0.5,0.25,0.75],
    [0,0.25,0.55],
    [0.5,0.25,0.75],
    [1,0.25,0.75],
    [0.5,0.25,0.75],

    [0.5,0.25,1],
    [0.25,0.25,1.15],
    [0.5,0.25,1.25],
    [0.75,0.25,1.15],
    [0.5,0.25,1],
    [0.5,0.25,0.75],

    ])



stream = autoStream()
HEIGHT, WIDTH = next(stream)[1].shape[:2]
size = WIDTH,HEIGHT

K = kgen(size,1.7) # fov aprox 60 degree

marker = np.array(
       [[0,   0,   0],
        [0,   1,   0],
        [0.5, 1,   0],
        [0.5, 0.5, 0],
        [1,   0.5, 0],
        [1,   0,   0]])



def polygons(cs,n,prec=2):
    rs = [ redu(c,prec) for c in cs ]
    return [ r for r in rs if len(r) == n ]


def rots(c):
    return [np.roll(c,k,0) for k in range(len(c))]


def bestPose(K,view,model):
    poses = [ Pose(K, v.astype(float), model) for v in rots(view) ]
    return sorted(poses,key=lambda p: p.rms)[0]  

# Direccion en la que se mueve el muñeco
reverse = False

for key,frame in stream:
    key = cv.waitKey(1) & 0xFF
    if key == 27: break
    
    
    g = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    cs = extractContours(g, minarea=5, reduprec=2)

    good = polygons(cs,6,3)

    poses = []
    for g in good:
        pos = bestPose(K,g,marker)
        if pos.rms < 2:
            poses += [pos.M]

    cv.drawContours(frame,[htrans(M,marker).astype(int) for M in poses], -1, (0,255,255), 1, lineType)
    cv.drawContours(frame,[htrans(M,cube/2).astype(int) for M in poses], -1, (0,255,0), 1, lineType)
    
    cv.drawContours(frame, [htrans(M,persona/3).astype(int) for M in poses], -1, (255,0,0), 3, lineType)
    
    # Direccion del muñeco
    if not reverse:
        persona = persona+ [0,incrementoMov,0]
        if persona[0][1] >= 1:
            reverse = True
    else:
        persona = persona - [0,incrementoMov,0]
        if persona[0][1] <= 0:
            reverse = False
            

    cv.imshow('Realidad Aumentada',frame)