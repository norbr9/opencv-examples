#!/usr/bin/env python3

# Reconocimiento de objetos usando sus "descriptores"
# Uso de SIFT, método para extraer puntos de interés

# Uso del programa:
# c : añade la iamgen a la lista de modelos a comparar
# v : comprueba si el frame actual se corresponde con algun modelo previamente
# guardado, si es asi imprime por pantalla el frame y su modelo
# x : limpia la lista de modelos a comparar



import cv2 as cv
import time

from umucv.stream import autoStream
from umucv.util import putText

# Filtro para SIFT en regiones de bajo contraste
# cuando mayor es el filtro más "features" son detectadas
CONTRAST_THRESHOLD = 0.05


# Scale invariant feature transfrom
sift = cv.xfeatures2d.SIFT_create(nfeatures=0,
                                  contrastThreshold=CONTRAST_THRESHOLD)

# buscador de coincidencias por fuerza bruta
matcher = cv.BFMatcher()  

# Lista para guardar los modelos de la forma (keypoints,descriptors,image)
models = []


def cleanModelWindows():
    for window in range (0,len(models)+1):
        cv.destroyWindow("Model" + str(window))
    

for key, x in autoStream():
    
    # Vaciar la lista de modelos
    if key == ord('x'):
        cleanModelWindows()
        models = []
       

    t0 = time.time()
    keypoints , descriptors = sift.detectAndCompute(x, mask=None)
    t1 = time.time()
    putText(x, '{}  {:.0f}ms'.format(len(keypoints), 1000*(t1-t0)))

    # añadimos una imagen de referencia, con sus puntos y descriptores
    if key == ord('c'):
        models.append((keypoints, descriptors, x));
        
    
    # Mostramos por pantalla la camara
    flag = cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    cv.drawKeypoints(x,keypoints,x, color=(100,150,255), flags=flag)
    cv.imshow('CAM', x)
        

    
    if key == ord('v'):
        cleanModelWindows()
        
        # Si hay modelos para comparar
        if models:
    
            # Numero de modelo
            modelCount = 0
            
            # Mejor modelo encontrado
            bestModelTest = []
            bestModel = None
            bestModelN = 0
            
            # Para cada modelo comprobamos si se ajusta a la imagen actual
            t2 = time.time() # Para calcular el tiempo
            for m in models:
                
                # metodo knn (k-nearest neigbors)
                matches = matcher.knnMatch(descriptors, m[1], k=2)  # dame las dos mejores coincidencias
                
                good = []
                for mat in matches:
                    if len(mat) >= 2:
                        best,second = mat
                        # ratio test, se descartan los puntos cuya mejor coincidencia es parecida a la
                        # segunda mejor
                        if best.distance < 0.75*second.distance:
                            good.append(best)
                
                # Nos quedamos con el mejor modelo
                if len(good) > len(bestModelTest):
                    bestModel = m
                    bestModelTest = good
                    bestModelN = modelCount
                
                modelCount +=1
                
            t3 = time.time() # Fin calculo del tiempo
            
            # Mostrar por pantalla el modelo que más se ajusta a la imagen
            # si lo hubiese
            if bestModel != None:
                imgm = cv.drawMatches(x, keypoints, bestModel[2], bestModel[0], bestModelTest,
                                      flags=0,
                                      matchColor=(128,255,128),
                                      singlePointColor = (128,128,128),
                                      outImg=None)
                
                
                print("El frame se ha clasificado con el modelo " + str(bestModelN))
                putText(imgm ,'{} {:.0f}ms'.format(len(bestModelTest),1000*(t3-t2)), (150,16), (200,255,200))            
                cv.imshow("Model" + str(bestModelN),imgm)

