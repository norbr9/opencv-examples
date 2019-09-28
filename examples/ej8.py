#!/usr/bin/env python


########## Uso del programa ##################################
#   1 : Aumentar o reducir brillo                            #
#   2 : Imagen doble                                         #
#   3 : Bordes horizontales                                  #
#   4 : Bordes verticales                                    #
#   5 : Suavizado Gaussiano                                  #
#   x : Elimina el ROI seleccionado                          #
#   q : Elimina el filtro del ROI                            #
#	↑ : Aumenta el valor de filtro							 #
#	↓ : Disminuye el valor de filtro						 #
##############################################################



import numpy             as np
import cv2               as cv
import scipy.signal      as signal
import time

# Teclas
BRILLO = '1'
DOBLE  = '2'
BHOR   = '3'
BVER   = '4'
SGAU   = '5'
UP     = 82
DOWN   = 84

# Color
BLUE = (255,0,0)


# Coordenadas del ROI
xi = yi = xf = yf = -1

# Variables de control para el ROI
selection = False
isDrawing = False

# Almacenamiento de imagenes obtenidas
frame = None
capture = None

# Variables para el control del filtro
filterValue = 0
InitFilterValue = True


# Funciones para transformacion inicial de la imagen
def rgb2gray(img):
    return cv.cvtColor(img,cv.COLOR_RGB2GRAY)

def gray2float(img):
    return img.astype(float) / 255

def frame2gray(capture):
	ret, frame = capture.read()
	return gray2float(rgb2gray(frame))


# Matriz de convolución
def cconv(k,x):
    return signal.convolve2d(x, k, boundary='symm', mode='same')


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

# Caputara de eventos del raton para obtener el ROI
def captureMouse(event, x, y, flags, param):
	global xi,yi,xf,yf,isDrawing,frame, selection, capture, lastRoi

            
    # Boton izquierdo raton
	if event == cv.EVENT_LBUTTONDOWN:
		xi = xf = x
		yi = yf = y
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
			
			# Trata el ROI
			lastRoi = tratarCordROI()

			#Mostrar el ROI
			cv.imshow('ROI', lastRoi)

# Dibujar un rectangulo como si fuera el ROI
def drawRectROI(f, xi, yi, xf, yf, color):
	cv.rectangle(f, (xi, yi), (xf, yf), color)

#Imprime el texto en pos
def printText(frame, text, pos):
		cv.putText(frame, text, pos, fontFace=cv.FONT_HERSHEY_COMPLEX , fontScale=0.55, color=255) 

# FPS
def getFps(nFrames, startTime):
	fps = nFrames / (time.time() - startTime)
	return round(fps, 2)

# Devuelve el valor inicial del filtro
def getvInicial(selectedKey):
	value = 0
    
	if selectedKey == BRILLO:
		value = 1.6

	if selectedKey == DOBLE:
		value = 3

	if selectedKey == BHOR or selectedKey == BVER or selectedKey == SGAU:
		value =  1

	return value

# Tratamiento del usos de las flechas para aumentar o reducir
def cambiarFilterValue(selectedKey, key):
	global filterValue
    
    # Brillo
	if selectedKey == BRILLO:
		if key == UP: 
			return filterValue + 0.2
		if key == DOWN: 
			return filterValue - 0.2
    
    # Resto de filtros
	elif selectedKey == DOBLE or selectedKey == BHOR or selectedKey == BVER or selectedKey == SGAU:
		if key == UP: 
			return filterValue + 1
		if key == DOWN: 
			return filterValue - 1

	return filterValue

# Matriz de convolución con el filtro
def getMatrizConv(selectedKey):
	global filterValue

	#Brillo
	if selectedKey == BRILLO:		
		if filterValue <= 0:
			filterValue = 0
		ker = np.array([[ 0, 0, 0]
						,[ 0, filterValue, 0]
						,[ 0, 0, 0]])

	#Imagen doble
	elif selectedKey == DOBLE:	
		
		if filterValue <= 1:
			filterValue = 1

		ker = np.zeros([filterValue,filterValue])
		ker[0,0] = 1
		ker[filterValue-1,filterValue-1] = 1
		ker = ker/np.sum(ker)

	#Bordes horizontales
	elif selectedKey == BHOR: 
		ker = np.array([[ 0, 0, 0]
						,[ -filterValue, 0, filterValue]
						,[ 0, 0, 0]])

	#Bordes verticales
	elif selectedKey == BVER: 
		ker = np.array([[ 0, -filterValue, 0]
						,[ 0, 0, 0]
						,[ 0, filterValue, 0]])

	return ker

#Aplica el suavizado Gaussiano a una imagen
def gaussianBlur(frameFiltro):
	global filterValue
	
	if filterValue <= 1:
		filterValue = 1

	return cv.GaussianBlur(frameFiltro, (0,0), filterValue)


def numAsFilterName(fnum):
    filter = ""
    
    if fnum == BRILLO:
        filter = "BRILLO"
    elif fnum == DOBLE:
        filter = "DOBLE"
    elif fnum == BHOR:
        filter = "BORDE HORIZONTAL"
    elif fnum == BVER:
        filter = "BORDE VERTICAL"
    elif fnum == SGAU:
        filter = "SUAVIZADO GAUSSIANO"

    return filter        
        

#Aplica el filtro correspondiente al ROI seleccionado
def aplicarFiltro(capture, xi, yi, xf, yf, selectedKey, key):
	global filterValue

	frameFiltro = frame2gray(capture)

	#Dibuja ROI al que aplicar el filtro
	if selection:
		drawRectROI(frameFiltro, xi, yi, xf, yf, (255,0,0))

	#Si es la primera vez que se inicia
	if InitFilterValue:
		filterValue = getvInicial(selectedKey)

	#Aumenta/reduce el valor del filtro
	filterValue = cambiarFilterValue(selectedKey, key)

    # Si no se aplica el suavizado Gaussiano 
    # se calcula la matriz de convolucion

	if selectedKey != SGAU:
		ker = getMatrizConv(selectedKey)
		frame = cconv(ker, frameFiltro[yi:yf, xi:xf])
	else:
		frame = gaussianBlur(frameFiltro[yi:yf, xi:xf])

	
	frameFiltro[yi:yf, xi:xf] = frame
	text = numAsFilterName(selectedKey) + ": " + str(round(filterValue, 1))

	return frameFiltro, text

			

cv.namedWindow("cam")
cv.setMouseCallback("cam", captureMouse)	

capture = cv.VideoCapture(0)

seg = 1					
nFrames = 0				
fps = 0		
selectedKey = ''
startTime = time.time()		
while(True):
	key = cv.waitKey(1) & 0xFF

	if key == 27: break
	

	#Tecla x para hacer desaparecer el ROI y el filtro
	if key == ord('x'):		
		selection = False
		selectedKey = ''
		InitFilterValue= True
            
    # Q para qutiar el ROI pero dejar el filtro
	if key == ord('q'):		
		selectedKey = ''
		InitFilterValue= True

    # Obtener frame en tone de grises
	frame = frame2gray(capture)

	# Si hay ROI se dibuja
	if selection:
		drawRectROI(frame, xi, yi, xf, yf, BLUE)

	#Filtros
	if selectedKey == BRILLO or key == ord(BRILLO):
		selectedKey = BRILLO
		frame, text = aplicarFiltro(capture, xi, yi, xf, yf, selectedKey, key)

	elif selectedKey == DOBLE or key == ord(DOBLE):
		selectedKey = DOBLE
		frame, text = aplicarFiltro(capture, xi, yi, xf, yf, selectedKey, key)

	elif selectedKey == BHOR or key == ord(BHOR):
		selectedKey = BHOR
		frame, text = aplicarFiltro(capture, xi, yi, xf, yf, selectedKey, key)

	elif selectedKey == BVER or key == ord(BVER):
		selectedKey = BVER
		frame, text = aplicarFiltro(capture, xi, yi, xf, yf, selectedKey, key)

	elif selectedKey == SGAU or key == ord(SGAU):
		selectedKey = SGAU
		frame, text = aplicarFiltro(capture, xi, yi, xf, yf, selectedKey, key)


	#Imprime información del filtro
	if selectedKey != '' and selection:
		printText(frame, text, pos=(5, 40))
		InitFilterValue = False

	#FPS 
	nFrames += 1
	if ((time.time() - startTime) > seg):
		fps = getFps(nFrames, startTime)
		nFrames = 0
		startTime = time.time()

	printText(frame, "FPS: " + str(fps), pos=(5, 20)) 


	cv.imshow('cam', frame)


cv.destroyAllWindows()
