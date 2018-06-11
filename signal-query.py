# -*- coding: utf-8 -*-
"""
Spyder Editor
"""

import serial

# Open serial port and set parameters
ser = serial.Serial('COM4')
if ~ser.is_open:
    ser.baudrate = 19200
    ser.timeout = 10 #seconds
    ser.bytesize=serial.EIGHTBITS
    ser.parity=serial.PARITY_NONE
    ser.strpbits=serial.STOPBITS_ONE

ser.write(b'AT +CSQ')

# Open file to write to
cmdlog = open("cmdfile.txt","w")
