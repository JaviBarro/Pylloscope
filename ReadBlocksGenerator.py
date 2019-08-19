# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 19:35:31 2019

@author: Javi
"""

import serial
import Parameters
import numpy as np

def SerialReader(ser):
    # Yields a dictionary containing 'success' = [True | False] and 'data' = np.array

    # initialization consists of finding the start of a socket.
    # We recognize it by the start flag and the socketSize.
    # We define a number of coincidences (flag found right after the end of a
    # socket) as enough to consider missidentification probability to be "very
    # low".
    NCoincidences = 3
    
    foundStarts = 0
    while foundStarts < NCoincidences:
    
        # Read until we find the Flag. (max t=timeout or maxSize Bytes)

        arr = np.empty(1)
        while 127 != arr[-1]:
            print "buscando flag"
            bytesIter = ser.read(1)
            arr = np.frombuffer(bytesIter, dtype = "uint8")
            print arr[0]
        
        print "Flag Encontrado"
        # Next we read the size and check if there's another flag starting a new socket.
        socketSize = ord(ser.read())
        print "next char: " + str(socketSize)
          
        
        # We create an array with the information of one socket
        socket_i = np.array([socketSize])
        socket_i = np.append(socket_i, np.frombuffer( ser.read(size=socketSize-1), dtype="uint8" ))
        
        # We check if the last Byte is the Flag again.
        if 127 != socket_i[-1]:
            # Error. found Flag was part of the content.
            foundStarts = 0
            print "falso flag, comenzando de nuevo"
        else:
            foundStarts = foundStarts + 1
            print "Otro flag: foundStarts = " + str(foundStarts)
            
    # When initialized, we start reading, processing and yielding sockets
    while socketSize == socket_i.size:

        yield processBlock(socket_i)
        socket_i = np.frombuffer(ser.read(size=socketSize), dtype="uint8")
        #socket_i.flags.writeable = True # No sé por qué aparece como read-only. Si esto diera problemas, hacer una copia del vector y trabajar sobre ella.
        #socket_i[socket_i<0] = 256 + socket_i[socket_i < 0]
        
    yield {'success':False, 'data':[], 'faliure':'final de trama o cambio de tamaño de trama'}

    
    
    
    
def processBlock(socket):
    #We check the protocol mode and call the corresponding function.
    
  
    print ""
    print "socket : "
    print socket
        
    #skSize = socket[0]
    skMode = socket[1]
    
    # 200 incluye un diccionario de datos de 4 Bytes (8 medios bits)
    if skMode == 200:
        print "mode = 200"
        dictSuccessNdata = processBlock_m200(socket)
    else:
        dictSuccessNdata = {'success':False, 'data':[], 'faliure':'modo de protocolo SASCOP no se reconoce o no implementado'}
        
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
    print "Comprobando checksum"
    checkSum = np.sum(socket[0:socket[0]-2]) + socket[-1]
    
    checkSum = np.mod(checkSum, 256)
    if checkSum <> socket[-2]:
        print "error de checksum. Devolvemos diccionario con descripción"
        return {'success':False, 'data':[], 'faliure':'checkSum value not coincident'}
    
    # Leemos el diccionario de datos:4 bytes que describen el tamaño de 8 señales
    # (8 grupos de 4 bits)
    arrSignalsSize = [0, 0, 0, 0, 0, 0, 0, 0]
    j=0
    for i in range(0, 3): # i es el Byte leído del DD.
        #Primero la mitad más significativa y luego la menos significativa
        arrSignalsSize[j]=(socket[2+i] & 0xF0) >> 4
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
    iSingleSampleSize = np.sum(arrSignalsSize)
    if np.mod(iDataSize, iSingleSampleSize) != 0:
        print "Error: El Diccionario de datos describe " + str(iSingleSampleSize) + " Bytes"
        print " pero en el socket vienen " + str(iDataSize) + ". Se ignorarán los Bytes que sobren..."
    iNumSamples = iDataSize / iSingleSampleSize
    
    # Creamos la matriz a devolver. Primero con ceros:
    npaData = np.zeros((iNumSamples, iNumSignals), dtype=np.int64)
    
    # We calculate the values of the signals
    iBuff = 7-1 # Apunta a los Bytes del socket en los que empieza cada Dato
    # El primero es el 7º, que es el índice 6, porque antes están: 1B size, 1B mode, 4B DataDict.
    # iData = 0 # Incrementa con cada dato para apuntar al 
    
    for sample in range(iNumSamples):
        for signal in range(iNumSignals):
            # Creamos un list comprehension con los valores de los Bytes correspondientes 
            # desplazados según lo significativo que sea cada uno.
            # BIG ENDIAN
            dataComponents = [socket[iBuff + i] << (arrSignalsSize[signal] -1 - i)*8 for i in range(arrSignalsSize[signal])]
            
            # Formamos el dato sumando todos los componentes
            npaData[sample, signal] = np.sum(dataComponents)
            iBuff += arrSignalsSize[signal]
    
    print "llegamos hasta el final. devolvemos true y data"    
    print "data: "
    print npaData
    print ""
    
    return {'success':True, 'data':npaData}



    