# ****************************************************
# * File         : GarduinoBase.py
# * Description  : Simple program for reading Garduino information and storing as CSV
# * Author       : Rowland Marshall
# * 
# * Versions     :
# *   2.00 | 2020-08-17 21:26:00 |  Fixed filename for CSV; removed print the countdown 
# *   1.00 | 2020-08-17 21:06:00 |  Version 1! logs to V1_00 csv.  Not ideal (triggers git...but it makes for an easy extraction) 
# *   0.04 | 2020-08-17 21:00:00 |  corrected the serial port to ttyUSB0
# *   0.03 | 2020-08-17 09:28:59 |  modifying to work on the beaglebone
# *   0.02 | 2020-08-02 16:50:50 |  restructure to make a permanent loop
# *   0.01 | 2020-08-02 14:55:22 |  initial build reading from serial and writing to csv
# ****************************************************/

# imports
import serial       # serial port comms
import time         # to wait (debugging)
from datetime import datetime #for timestamp


# initialise serial port
serialPort = serial.Serial(port = "/dev/ttyUSB0", baudrate  =9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
# initialise string variable
serialString = ""                           # Used to hold data coming over UART

serialString = serialPort.readline() #added this extra line to clear the buffer at the start
serialString = serialPort.readline() #added this extra line to clear the buffer at the start

sampleTime = 60 #only store every 60th value

while(True): #monitor indefinately
    # Wait until there is data waiting in the serial buffer
    # debug print(serialPort.in_waiting)
    if(serialPort.in_waiting > 0):
        # print(sampleTime) debug only
        if (sampleTime == 1):
            try:
                ## Initialise file write
                output_File=open("GarduinoOutput/garduinoOutputV2_00.csv",mode="a+",encoding="utf-8")
                #run a loop to write the buffer to the output file
                # Read data out of the buffer until a carraige return / new line is found
                # debug print(serialPort.in_waiting)
                serialString = serialPort.readline()

                # Print the contents of the serial data
                try:
                    output_File.write(datetime.now().isoformat() + ";")
                    output_File.write(datetime.now().strftime("%d/%m/%y") + ";")
                    output_File.write(datetime.now().strftime("%H:%M:%S") + ";")
                    output_File.writelines(serialString.decode('Ascii'))
                    #output_File.write("Successdecode\n")
                    output_File.close()
                except IOError:
                    output_File.write("decode error\n")
            except IOError:
                print("File not found or path is incorrect")
            sampleTime = 60
        else:
            serialString = serialPort.readline()
            sampleTime -= 1
print("exit")
serialPort.close()
