#Python (3.6.1), pyserial (3.4)

# Simple program to open a serial port

import time
import serial
import csv

# Initialization and open the port
ser = serial.Serial()

# Configure serial port parameters
# Windows 'COM#'  UNIX: "/dev/tty##" or "/dev/ttyUSB#"
ser.port = "COM4"

# Default is 9600,8,n,1,no timeout 
ser.baudrate = 19200
#ser.bytesize = serial.EIGHTBITS    #number of bits per bytes SEVEN or EIGHT
#ser.parity = serial.PARITY_NONE    #set parity check: NONE,EVEN,ODD
#ser.stopbits = serial.STOPBITS_ONE  
ser.timeout = None		    #block read, None,1,2
#ser.xonxoff = False                #disable software flow control
#ser.rtscts = False                 #disable hardware (RTS/CTS) flow control
#ser.dsrdtr = False                 #disable hardware (DSR/DTR) flow control
#ser.writeTimeout = 2               #timeout for write


#open .csv file to write to
with open('signaldata.csv', 'w', newline='') as csvfile:
    fieldnames = ['mast_offset','UTC_time_stamp','Iridium_time_stamp','signal_quality']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()


def send2serial(cmd):

  data = ""

  # flush all output data
  ser.flushOutput()

  # send the command to the serial port
  try:
      ser.write(cmd)
  except Exception as e:
      print ("Error: Can't send data to serial port: %s" % str(e) )
  else:
      try:
          echo = ser.readline().decode()
          data = ser.readline().decode()
          
      except Exception as e:
          print ("Error: Can't read data from serial port: %s" % str(e))
  return data


try: 
    ser.open()
except Exception as e:
    print("Error initializing serial port: ",str(e))

if ser.isOpen():

    try:
        count = int(input ("Number of Data Samples to Collect: "))
        
        #check if input is valid
        if count <= 0:
            print (" Invalid input. Please enter an integer greater than 0.")
            count = int(input ("Number of Data Samples to Collect: "))
        
        #start counter
        while count > 0:
            
            ser.flushInput()  #flush input buffer, discarding all its contents
            ser.flushOutput() #flush output buffer, aborting current output 
                          #and discard all that is in buffer

            #write data
            serialcmd=("AT +CSQ \r")
            response = send2serial(serialcmd.encode())

            if response:
                print ("Response: %s \n" % response )
            
                #include timestamp
                ts = time.gmtime()   #UTC timestamp in sec since epoch format
                st = time.strftime("%Y-%m-%d %H:%M:%S", ts) #convert to YMD, HMS format
                print ("UTC Timestamp: %s \n" % st)
                print ("-------------------------------------------")
                #Iridium network timestamp
                ints = send2serial("AT -MSSTM \r".encode()) # returned Iridium network time
                intsst = time.strftime("%Y-%m-%d %H:%M:%S", ints) #convert to YMD, HMS format
                #print ("Iridium Network Timestamp: %s \n" % intsst)
                
            count -= 1
            
            if count == 0:
                print ("Data collection complete")
                
        ser.close()
    except Exception as e1:
        print ("Error communicating...: ",str(e1))

else:
    print ("Error serial port not open ")