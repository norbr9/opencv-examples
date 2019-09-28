#!/usr/bin/env python

import numpy as np
import cv2   as cv
import sys


# Uso: python E15.py coins.png
# Tecla c para obtener medir de nuevo
# Ejercicio 15 : Rectifica la imagen de un plano para medir distancias usando coins.png


COLOR_LINEAS = (0,0,255)

# Medidas del carnet
ancho = 8.6
alto = 5.4
ratio = 1.6

# En la imagen
xv = 150
yv = 550
lado = 100

# Para leer el input
carnet = []
puntos = []

# leer coins.png
img = cv.imread(sys.argv[1], cv.IMREAD_COLOR)


def medirCarnet(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        punto = [x, y]
        carnet.append(punto)
        
        # Dibujar lineas en la imagen que forman el contorno del carnet
        cv.circle(img, (x, y), 5, COLOR_LINEAS, -1)
        if (len(carnet) == 2):
            cv.line(img, (carnet[0][0], carnet[0][1]), (carnet[1][0], carnet[1][1]), COLOR_LINEAS, 2)
        elif (len(carnet) == 3):
            cv.line(img, (carnet[1][0], carnet[1][1]), (carnet[2][0], carnet[2][1]), COLOR_LINEAS, 2)
        elif (len(carnet) == 4):
            cv.line(img, (carnet[2][0], carnet[2][1]), (carnet[3][0], carnet[3][1]), COLOR_LINEAS, 2)
            cv.line(img, (carnet[3][0], carnet[3][1]), (carnet[0][0], carnet[0][1]), COLOR_LINEAS, 2)
            
def medirPuntos(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        punto = [x, y]
        if len(puntos)< 2:
            puntos.append(punto)
        
            #Dibujar los puntos
            cv.circle(rec, (x, y), 5, COLOR_LINEAS, -1)
            
        if (len(puntos) == 2):
            cv.line(rec, (puntos[0][0], puntos[0][1]), (puntos[1][0], puntos[1][1]), COLOR_LINEAS, 2)
            
            # Teorema de pitagoras 
            if (puntos[0][0] >= puntos[1][0]):
                c1 = puntos[0][0] - puntos[1][0]
            else:
                c1 = puntos[1][0] - puntos[0][0]
                
            if (puntos[0][1] >= puntos[1][1]):
                c2 = puntos[0][1] - puntos[1][1]
            else:
                c2 = puntos[1][1] - puntos[0][1]
            
            dstPixel = np.sqrt(c1 * c1 + c2 * c2)
            
            cv.putText(rec, repr(dstPixel) + ' pixeles', (0, 50), cv.FONT_HERSHEY_SIMPLEX, 1, COLOR_LINEAS, thickness = 2)
            # Pixel a centimetro
            dstCm = dstPixel * alto / lado
            cv.putText(rec, repr(dstCm) + 'centimetros', (0, 75), cv.FONT_HERSHEY_SIMPLEX, 1, COLOR_LINEAS, thickness = 2)





real = np.array([
            [float(xv), float(yv)],
            [float(xv+lado*ratio), float(yv)],
            [float(xv+lado*ratio), float(yv+lado)],
            [float(xv), float(yv+lado)]])




dist = False
while True:
    key = cv.waitKey(1) & 0xFF
    if key == 27:
        break
    if key == ord('c') and dist:
        puntos = []
        rec = original.copy()
        
    
    cv.setMouseCallback("coins", medirCarnet)
    cv.imshow('coins', img)
    
    if not dist and len(carnet) == 4:
        view = np.array([
            [float(carnet[0][0]), float(carnet[0][1])],
            [float(carnet[1][0]), float(carnet[1][1])],
            [float(carnet[2][0]), float(carnet[2][1])],
            [float(carnet[3][0]), float(carnet[3][1])]])
    
        
        H = cv.findHomography(view, real)[0]
        original = cv.warpPerspective(img, H, (800, 800))
        rec = original.copy()
        dist = True
        
    elif dist :
        cv.setMouseCallback("rectificada", medirPuntos)
        cv.imshow('rectificada', rec)
      
        
 
cv.destroyAllWindows()
