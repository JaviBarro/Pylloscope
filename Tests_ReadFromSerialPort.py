# -*- coding: utf-8 -*-
"""
Created on Tue Jan 01 20:13:58 2019

@author: Javi
"""

"""
Prueba de lectura por puerto serie desde la tarjeta MSP-EXP430
"""
import serial
import numpy as np

ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM3'
ser.open()

print 'puerto abierto'

ser.flushInput()
ser.flushOutput()

# PRUEBA SIMPLE: LEER E IMPRIMIR
if False:
    for i in range(10):
      data_raw = ser.read(100)
      print("data found: " + data_raw)


# PROBAMOS A ALMACENAR LOS BYTES EN UN bytearray
data_array = bytearray()
if False:
    for i in range(100):
        data_array.append( ser.read(1)  ) #Lectura sin buffer. Sólo para pruebas
    
    print data_array


# PROBAMOS A LEER DIRECTAMENTE DENTRO DE UN  NP.ARRAY()
if False:
    arr =  np.frombuffer(ser.read(100), dtype='byte')
    print arr


# PROBAMOS LECTURA EN BUCLE INCREMENTANDO EL ARRAY.

if True:     
    arr = np.empty(0)
    for i in range(10):
        print i
        arr = np.append(arr, np.frombuffer(ser.read(20), dtype='byte'))
            
    print arr
# hasta aqui funcionan todas las pruebas.
# La tarjeta envía primero el byte más significativo cuando se envían números
# de más de un byte.



print 'cerrando puerto'
ser.close() 
print 'puerto cerrado'