#!/usr/bin/env python

import cv2 as cv
import numpy as np
import sys

# Uso: python E16.py img0 img1 imgN
# img es una imagen que se encuentra en la ruta relativa images/img

# Crea una imagen paronamica atraves de otras imagenes
# es necesario introducir las imagens en orden (izquierda a derecha)


#lista para las imagenes
args = []

# Puntos de interes y descriptores
sift = cv.xfeatures2d.SIFT_create(nfeatures=0, contrastThreshold=0.1)	

# Matcher (fuerza bruta)
matcher = cv.BFMatcher()	


# Lee las imagenes y las transforma a tonos de grises
def tratInicial(file):
	img = cv.cvtColor( cv.imread('images/'+file), cv.COLOR_BGR2RGB) 
	return cv.cvtColor(img,cv.COLOR_RGB2GRAY)


# Transformación h a la imagen img
def t(h,img):
    return cv.warpPerspective(img, desp((50,150)) @ h,(1800,600))


# Desplazamiento
def desp(desp):
	dx,dy = desp
	return np.array([
			[1,0,dx],
			[0,1,dy],
			[0,0,1]])


# Mejores coincidencias de los descriptores de la imagen
def ratioTest(des1, des0):
	#coincidencias
	good = []	

	matches = matcher.knnMatch(des1, des0, k=2)

	#Mejor coincidencia
	for m in matches:
		best, second = m
		if best.distance < 0.75 * second.distance: 
			good.append(best)

	return good

#Combina dos imagenes
def union(img1, img2, H): 
	return np.maximum(t(np.eye(3),img2), t(H,img1))

#Crea una imagen panorámica a partir de la lista de imágenes pasada como parámetro
def panoramica(imagenes):
    # Primera imagen
	img1 = tratInicial(imagenes[0])
    
    
    # Para todas las demas imagenes, formar la panoramica
	for i in range(1, len(imagenes)):
		img2 = tratInicial(imagenes[i])

		#Obtenemos los vectores de descriptores
		(kps, des0) = sift.detectAndCompute(img1, None)
		(kps2, des1) = sift.detectAndCompute(img2, None)

		
		#lista de las mejores coincidencias de las imágenes
		good = ratioTest(des1, des0)	

		#Arrays que necesita findHomography
		src_pts = np.array([ kps [m.trainIdx].pt for m in good ]).astype(np.float32).reshape(-1,2)
		dst_pts = np.array([ kps2[m.queryIdx].pt for m in good ]).astype(np.float32).reshape(-1,2)

		H, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 3)

		img1 = union(img1, img2, H)

	return img1 





#Argumentos (imagenes)
args = sys.argv

# Elimino el primero que no corresponde a ninguna imagen
args.pop(0)	

# Realizar panoramica
img = panoramica(args)


cv.namedWindow("Panoramica")

# Mostrar panoramica
while(True):
	key = cv.waitKey(1) & 0xFF

	if key == 27: break
			
	cv.imshow('Panoramica',img)
		
		
cv.destroyAllWindows()