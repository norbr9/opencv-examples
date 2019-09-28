#!/usr/bin/env python

import cv2          as cv
from umucv.stream import autoStream
from umucv.util import putText


COLOR_LINEAS = (0,255,255)


# Para las coincidencias
sX = 0
sY = 0

stream = autoStream()

# Para calcular el centro de la imagen
height, width = next(stream)[1].shape[:2]
centroImg = (height//2,width//2)

medir = True
for key,frame in stream:
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Obtener las esquinas
    # Si hay mucha perdida (lost) tambien se recalculan
    if medir or key == ord('c') or len(corners)/2<=lost:
        corners = cv.goodFeaturesToTrack(gray, 50, 0.1, 10).reshape(-1,2)
        nextPts = corners
        prevgray = gray
        medir = False
    
    # Flujo optico del frame actual y la imagen obtenida
    nextPts, status, err = cv.calcOpticalFlowPyrLK(prevgray, gray, nextPts, None)
    lost=0
    prevgray = gray

    # Sumar vectores en el caso de que las coincidencias sean buenas
    # Si no aumentar la perdida
    for (x,y), ok, (x0,y0) in zip(nextPts, status, corners):
        if ok:
            sX += x - x0
            sY += y - y0
        else:
            lost +=1
    
    # Calcular distancia media
    tam = len(corners)
    distMedia = (int(-sX/tam),int(sY*-1/tam))
    
    #Longitud de la flecha a dibujar
    finArrow = (distMedia[0] + centroImg[0], distMedia[1] + centroImg[1])
    
    # Circulo en el centro de la imagen
    cv.circle(frame, centroImg, 2, COLOR_LINEAS, -1, cv.LINE_AA)	
    
    # Flecha indicando la direccion de la imagen
    cv.arrowedLine(frame, centroImg, finArrow, COLOR_LINEAS, 1, cv.LINE_AA)	

    # Reinciar las sumas de las coincidencias
    sX = 0
    sY = 0
    
    putText(frame, 'Esquinas : {}'.format(len(corners)), (5,20), color=COLOR_LINEAS)
    cv.imshow('Rotacion',frame)
    

cv.destroyAllWindows()
