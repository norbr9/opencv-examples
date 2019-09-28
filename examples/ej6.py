#!/usr/bin/env python

########## Uso del programa ##################################
#   Detector de objetos similares basado en el histograma.   #
#   Se usa el raton para marcar el ROI, este aparecera azul  #
#   cuando se encuentre un objeto similar, en otro caso      #
#   el color será verde.                                     #
##############################################################


import cv2 as cv
import numpy as np
import datetime


# Cordenadas del ROI
xi = yi = xf = yf = -1

#Máxima diferencia permitida entre histogramas
MAX_DIF = 0.4

# Variables de control para el ROI
selection = False
isDrawing = False


# Almacenamiento de imagenes obtenidas
roiList = list()
lastRoi = None
frame = None
capture = None

# Colores para dibujar el ROI
BLUE = (255,0,0)
GREEN = (0,255,0)


# Función para ordenar las cordenadas que contiene el ROI
def tratarCordROI():
	global xi,yi,xf,yf,frame

	# Ancho y alto del frame
	width = capture.get(3)
	height = capture.get(4)

	
    # Establecer valores en función de si es mayor o menor
	if xi > xf:
		aux = xi
		xi = xf
		xf = aux

	if yi > yf:
		aux = yi
		yi = yf
		yf = aux

	# Si la iamgen esta fuera de los margenes, la pongo dentro
	if xi < 0:
		xi = 0
	if yi < 0:
		yi = 0

	if xf > width:
		xf = int(width)
	if yf > height:
		yf = int(height)


	return frame[yi:yf, xi:xf]



# Histograma normalizado de una imagen
def histogram(image):
	h = cv.calcHist([image],
					[0, 1, 2],
					None,
					[8, 8, 8],
					[0,256]+[0,256]+[0,256])

	his = h / np.sum(h)  # normalizacion

	return his


# Caputara de eventos del raton para obtener el ROI
def captureMouse(event, x, y, flags, param):
	global xi,yi,xf,yf,isDrawing,frame, roiList, selection, capture, lastRoi


    # Boton izquierdo raton
	if event == cv.EVENT_LBUTTONDOWN:
		xi = x
		yi = y
		xf = x
		yf = y
		isDrawing = True
		selection = True	
        
    # Mover raton
	elif event == cv.EVENT_MOUSEMOVE:
		if isDrawing:
			xf = x
			yf = y
	
    
    # Dejar de pulsar boton izquierdo
	elif event == cv.EVENT_LBUTTONUP:
		if isDrawing:
			isDrawing = False
			xf = x
			yf = y

			# Normalizar las cordenadas
			lastRoi = tratarCordROI()
			
			#Guardar el ROI en la lista
			roiList.append(lastRoi)

			#Mostrar el ROI
			cv.imshow('ROI', lastRoi)

# Dibujar un rectangulo como si fuera el ROI
def drawRectROI(f, xi, yi, xf, yf, color):
	cv.rectangle(f, (xi, yi), (xf, yf), color)

# Diferencia entre los histogramas del frame actual y el del ROI
def difHistograms(frameAct, roi):
	hframeAct = histogram(frameAct)
	hroi = histogram(roi)

	return cv.compareHist(hroi, hframeAct, cv.HISTCMP_CHISQR)






cv.namedWindow("cam")
cv.setMouseCallback("cam", captureMouse)
capture = cv.VideoCapture(0)


while(True):
	key = cv.waitKey(1) & 0xFF

	if key == 27: break
	
    # Pulsar x para eliminar el ROI de la lista
	if key == ord('x'):
		selection = False
		roiList = roiList[:-1]


	ret, frame = capture.read()

		
    # Si hay algún ROI seleccionado
	if selection:
        # Si se encuentra un objeto igual se va a dibujar un rectagulo azul
		color = BLUE;

        # Si hay un ROI se obtiene la imagen
		if lastRoi is not None:
			fAct = tratarCordROI()
			diferencia = difHistograms(fAct, lastRoi)

			#Si el objeto no es el del ROI el rectangulo es verde
			if diferencia >= MAX_DIF:
				color =  GREEN

		#Dibujar rectangulo
		drawRectROI(frame, xi, yi, xf, yf, color)

	cv.imshow('cam',frame)
		
    
    # Guardar ROIs en disco
	if key == ord('s'):
		count = 1
		for r in roiList:
			fname = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
			cv.imwrite(fname+' '+str(count)+'.png',r)
			count += 1

        # Si se guarda, inicializar las variables del ROI
		selection = False
		roiList.clear()


cv.destroyAllWindows()
