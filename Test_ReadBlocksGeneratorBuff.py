# -*- coding: utf-8 -*-
"""
Created on Sat Feb 02 20:47:20 2019

@author: Javi
"""

import ReadBlocksGenerator as RB
# Creamos una clase que haga de Serial port:
# debe implementar read(size=1) y read_until()

def puertoSerieDummy():
    
    arr = [127, 78, 200,
            (4<<4) + 2, (2<<4) + 2, 0, 0,  #8 medios bytes: 4, 2, 2, 2, 0, 0, 0, 0
            0, 255, 127, 1,   0, 12,   1,0,   0, 1, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 2, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 3, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 4, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 5, 
            0, 255, 127, 1,   0, 12,   1,1,   0, 6, 
            0, 255, 127, 1,   0, 12,   1,2,   0, 7]
    
    arr.append(sum(arr)%256)
            
    arr2 = [127, 78, 200,
            (4<<4) + 2, (2<<4) + 2, 0, 0, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 8, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 9, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 10, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 11, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 12, 
            0, 255, 127, 1,   0, 12,   1,1,   0, 13, 
            0, 255, 127, 1,   0, 12,   1,2,   0, 14]
    arr2.append(sum(arr2)%256)
            
    arr = arr + arr2
    
    arr2 = [127, 78, 200,
            (4<<4) + 2, (2<<4) + 2, 0, 0, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 15, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 16, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 17, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 18, 
            0, 255, 127, 1,   0, 12,   1,0,   0, 19, 
            0, 255, 127, 1,   0, 12,   1,1,   0, 20, 
            0, 255, 127, 1,   0, 12,   1,2,   0, 21,
            
            ]
    arr2.append(sum(arr2)%256)
            
    arr = arr + arr2
    
    return buffer(bytearray(arr))


if __name__ == "__main__":
    serport = puertoSerieDummy()
    lector = RB.SerialReader(serport)
    
    for dicc in RB.SerialReader(serport):
        print ""
        print ""
        print dicc["success"]
        print dicc["data"]
    
#ser = serial.Serial()
#ser.baudrate = 9600
#ser.port = 'COM3'
#ser.timeout(3.0)
#ser.open()
