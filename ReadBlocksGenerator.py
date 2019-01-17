# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 19:35:31 2019

@author: Javi
"""

import serial
import Parameters
import numpy as np

def SerialReader(portName):
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 'COM3'
    ser.timeout(3.0)
    ser.open()
    
    
    # initialization consists of finding the start of a socket.
    # We recognize it by the start flag and the socketSize.
    # We define a number of coincidences (flag found right after the end of a
    # socket) as enough to consider missidentification probability to be "very
    # low".
    NCoincidences = 3
    
    foundStarts = 0
    while foundStarts < NCoincidences:
    
        # Read until we find the Flag. (max t=timeout or maxSize Bytes)
        lastByte = 0    
        while 127 != lastByte:
            lastByte = ser.read_until(Parameters.flag, Parameters.maxSize)
            
        # Next we read the size and check if there's another flag starting a new socket.
        socketSize = ser.read()
        
        socket_i = np.array([socketSize])
        socket_i = np.append(socket_i, np.frombuffer( ser.read(size=socketSize-1) ))
        if 127 != socket_i[-1]:
            # Error. found Flag was part of the content.
            foundStarts = 0
        else:
            foundStarts = foundStarts + 1
            
            
    while socketSize == socket_i.size():
        yield processBlock(socket_i)
        socket_i = np.frombuffer(ser.read(size=socketSize))

    
    
    
        