# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 19:35:31 2019

@author: Javi
"""

import serial
import Parameters
import numpy as np

def SerialReader(portName):
    # Yields a dictionary containing 'success' = [True | False] and 'data' = np.array
    
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
        
        # We create an array with the information of one socket
        socket_i = np.array([socketSize])
        socket_i = np.append(socket_i, np.frombuffer( ser.read(size=socketSize-1) ))
        # We check if the last Byte is the Flag again.
        if 127 != socket_i[-1]:
            # Error. found Flag was part of the content.
            foundStarts = 0
        else:
            foundStarts = foundStarts + 1
            
    # When initialized, we start reading, processing and yielding sockets
    while socketSize == socket_i.size():
        yield processBlock(socket_i)
        socket_i = np.frombuffer(ser.read(size=socketSize))
        
    return {'success':False, 'data':[]}

    
    
    
    
def processBlock(socket):
    #We check the protocol mode and call the corresponding function.
    
    #skSize = socket[0]
    skMode = socket[1]
    
    # 200 incluye un diccionario de datos de 4 Bytes (8 medios bits)
    if skMode == 200:
        dictSuccessNdata = processBlock_m200(socket)
        
    return dictSuccessNdata
    


def processBlock_m200(socket):
    
    # 4Bytes for a simple 8 signals data dictionary: every 4 bits
    # determine the size of one of the signals. A signal with size 0
    # means that it does not exist / it is not being sent.
    #
    # 0 => Size
    # 1 => Mode (200)
    # 2 => Data Dictionary Byte 1
    # 3 => Data Dictionary Byte 2
    # 4 => Data Dictionary Byte 3
    # 5 => Data Dictionary Byte 4
    # 6 => Raw Information Byte 1
    # 7 => Raw Information Byte 2
    # 8 => Raw Information Byte 3
    # ...
    # size - 1 => checksum
    # size => Flag
    checkSum = np.sum(socket)
    checkSum = np.mod(checkSum, 256)
    if checkSum <> socket[-2]:
            return {'success':False, 'data':[], 'faliure':'checkSum value not coincident'}
    
    arrSignalsSize = [0, 0, 0, 0, 0, 0, 0, 0]
    j=0
    for i in range(0, 3):
        #Primero la mitad más significativa y luego la menos significativa
        arrSignalsSize[j]=socket[2+i] & 0xF0
        j=j+1
        arrSignalsSize[j]= socket[2+i] & 0x0F
        j=j+1
        
    # calculamos el número de señales
    iNumSignals = np.count_nonzero(arrSignalsSize)
        
    # Calculamos el número de mediciones:
    iSkSize = socket[0]
    # dataSize = socketSize - 8 Bytes:
    # [Flag], mode, size, 4*DataDictionary,RawData, checksum. (Flag va al final, Después del Checksum)
    iDataSize = iSkSize - 8
    iNumSamples = iDataSize / np.sum(arrSignalsSize)
    
    # Creamos la matriz a devolver. Primero con ceros:
    npaData = np.zeros((iNumSamples, iNumSignals), dtype=np.int64)
    
    # We calculate the values of the signals
    iBuff = 6-1 # Apunta a los Bytes del socket en los que empieza cada Dato
    # iData = 0 # Incrementa con cada dato para apuntar al 
    
    for sample in range(iNumSamples):
        for signal in range(iNumSignals):
            # Creamos un list comprehension con los valores de los Bytes correspondientes 
            # desplazados según lo significativo que sea cada uno.
            dataComponents = [socket[iBuff + i] >> (arrSignalsSize[signal]-i) for i in range(arrSignalsSize[signal])]
            
            # Formamos el dato sumando todos los componentes
            npaData[sample, signal] = np.sum(dataComponents)
        
    return {'success':True, 'data':npaData}
    