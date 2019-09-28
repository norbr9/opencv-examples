#!/usr/bin/env python

import cv2   as cv
import numpy as np
import time

from datetime import datetime
from umucv.stream import autoStream

# Numero maximo de frames mientras no esta capturando movimiento
# Es necesario ya que si los frames son muy parecidos nunca va a detectar
# movimiento porque apenas hay diferencia entre ellos.
MAX_FRAMES = 10

# VaribleS de control para esperar MAX_FRAMES
isRecording = False
frames = 0

# Array de frames para detectar diferencias entre ellos
static_frames = []

for key,frame in autoStream():
    if not isRecording:
        frames += 1
        if frames == MAX_FRAMES:
            frames = 0
            isRecording = True

        cv.imshow("cam",frame)
        continue

    # Inicializar motion a 0 (no hay movimiento)
    motion = 0

    # Convertir imagen a gray_scale
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)


    # Convertir imagen gray a GaussianBlur
    # Para poder encontrar cambios facilmente
    gray = cv.GaussianBlur(gray, (21, 21), 0)

    # Si estamos en la primera iteración inicilizamos el frame
    if not static_frames:
        static_frames.append(gray)
        static_frames.append(gray)
        continue

    # Frame actual
    static_frames[1] = gray

    # Diferencia entre el frame anterior
    # y la imagen actual
    diff_frame = cv.absdiff(static_frames[0], static_frames[1])


    thresh_frame = cv.threshold(diff_frame, 30, 255, cv.THRESH_BINARY)[1]
    thresh_frame = cv.dilate(thresh_frame, None, iterations = 2)

    # Contorno de los objectos en movimiento
    cnts = cv.findContours(thresh_frame.copy(),
                        cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[1]

    # Detectamos si hay diferencia
    for contour in cnts:
        if cv.contourArea(contour) >= 1000:
            motion = 1
            break


    # El frame actual es el frame anterior
    # para la siguiente iteracion
    static_frames[0] = static_frames[1]


    cv.imshow('cam', frame)

    isRecording = False

    # Si no hay movimiento no hago nada
    if motion == 0:
        continue


    print('Movimiento')
    print(datetime.now())

cv.destroyAllWindows()

