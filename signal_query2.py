#Python (3.6.1), pyserial (3.4)

# Program to open a serial connection to the Iridium Edge modem and query 
# signal strength a given number of times.

import time
import datetime
import serial
import csv
import matplotlib.pyplot as plt

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
          # eliminate echo from initial read (turn off input echo on Edge?) 
          echo = ser.readline().decode()
          data = ser.readline().decode()
          
      except Exception as e:
          print ("Error: Can't read data from serial port: %s" % str(e))
  return data

# User input mast offset distance for testing
mastoff = input('Enter the mast offset from the gondola in inches: ')

try: 
    ser.open()
except Exception as e:
    print("Error initializing serial port: ",str(e))

#open date and time dependant .csv file to write to
datestring = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')    
    
with open('signaldata_' + datestring + '.csv', 'w', newline='') as csvfile:
    fieldnames = ['mast_offset','sample_number','UTC_time_stamp','signal_quality']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    if ser.isOpen():
    
        try:
            count = int(input ("Number of Data Samples to Collect: "))
            
            #check if input is valid
            if count <= 0:
                print (" Invalid input. Please enter an integer greater than 0.")
                count = int(input ("Number of Data Samples to Collect: "))
            
            #start counter
            while count > 0:
                
                run = 1 # counter for data collections
                ser.flushInput()  #flush input buffer, discarding all its contents
                ser.flushOutput() #flush output buffer, aborting current output 
                              #and discard all that is in buffer
    
                #write data
                serialcmd=("AT +CSQF \r") #signal query command
                response = send2serial(serialcmd.encode()).strip('+')
    
                if response:
                    print ("Response: %s \n" % response )
                
                    #include timestamp
                    ts = time.gmtime()   #UTC timestamp in sec since epoch format
                    st = time.strftime("%Y-%m-%d %H:%M:%S", ts) #convert to YMD, HMS format
                    print ("UTC Timestamp: %s \n" % st)
                    print ("-------------------------------------------")
                    #Iridium network timestamp
                    #ints = send2serial("AT -MSSTM \r".encode()) # returned Iridium network time
                    #intsst = time.strftime("%Y-%m-%d %H:%M:%S", ints) #convert to YMD, HMS format
                    #print ("Iridium Network Timestamp: %s \n" % intsst)
                    
                    #write data to .csv file
                    writer.writerow({'mast_offset': mastoff, 'run_number': run, 'UTC_time_stamp': st, 'signal_quality': response})
                    
                    #plot signal strength versus run number each 
                    plt.plot([run],[response], 'ro')
                    
                #wait 1 second
                time.sleep(1) #each collection should be 1 second after the last 
                    
                count -= 1
                run += 1
                
                if count == 0:
                    print ("Data collection complete; " + run + " samples collected.")
                    
            ser.close()
        except Exception as e1:
            print ("Error communicating...: ",str(e1))
    
    else:
        print ("Error serial port not open ")
        
# format and show plot
plt.xlabel('Run Number')
plt.ylabel('Signal Strength in bars (0-5)')
plt.title('Signal Strength over Time')
plt.show()