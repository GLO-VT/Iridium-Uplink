#Python (3.6.4), pyserial (3.4)

# Program to open and read from a set of .csv files to calculate the standard 
# deviation of data sets. The read data is plotted along with the standard
# deviation. A user input standard deviation limit will show the graphed data
# variation

import matplotlib.pyplot as plt
import csv
import math

run = 'y'
while run == 'y':
    
    datafile = input("Enter the .csv file you want to read from: ")
    
    with open(datafile) as csvfile:
        readCSV = csv.reader(csvfile, delimiter = ',')
        
        next(readCSV)
        count = 0
        sigdata = []
        datasum = 0
        
        for row in readCSV:
            offset = int(row[0])
            datasum += int(row[3])
            sigdata.append(int(row[3]))
            count += 1

        datamean = datasum / count
        diffsum = 0
        
        for i in range(len(sigdata)):    
            diffsum += (int(row[3]) - datamean)
            
        var = abs(diffsum / count)
        sigma = math.sqrt(var)

        plt.errorbar(offset, datamean, sigma, linestyle='None', marker='^')
    
    run = input("Add another data file to the set? Enter 'y' if yes, anything else if no: ")


plt.xlabel('Mast Offset (in)')
plt.ylabel('Signal Strength in bars (0-5)')
plt.title('Signal Strength vs. Mast Offset')
plt.axis([0,50,0,5])
plt.show()
plt.savefig('signalvsoffset.png')