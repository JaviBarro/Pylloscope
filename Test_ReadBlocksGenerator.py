# -*- coding: utf-8 -*-
"""
Created on Sat Feb 02 20:47:20 2019

@author: Javi
"""
import serial
from ReadBlocksGenerator import SerialReader
import numpy as np

        
if __name__ == "__main__":
    
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 'COM3'
    ser.open()    
    print "Puerto Abierto: " + ser.port
    #ser = puertoSerieDummy()
    
    ser.flushInput()
    ser.flushOutput()
    
    dctgen = SerialReader(ser)
    
    print ""
    print "comienza el bucle ppal: "
    for i in range(0, 10):
        dct = next(dctgen)
        print i, dct['success'], np.shape(dct['data'])
        if not dct['success']:
            print dct['faliure']
    
    ser.close()
    
    print ""
    print " End Of Program"
    
    