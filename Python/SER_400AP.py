##------------------------------------------------------------------------------------------------------------------
## Module: SER_400AP.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 06/29/2012)    :    Initial release
##    V1.1.0    (Thomas W. Heck, 11/12/2012)    :    Replaced timeout code, with method
##                                                   using time module
##    V1.1.1    (Thomas W. Heck, 11/21/2012)    :    Removed /dev/ from serial port path.
##    V2.1.0    (Thomas W. Heck, 01/29/2013)    :    Demo Release V2.1
##------------------------------------------------------------------------------------------------------------------

##------------------------------------------------------------------------------------------------------------------
## NOTES
##  1.)  Works with the following Plug-in Terminus models 
##            GSM865CF
##            CDMA864CF
##            HSPA910CF
##------------------------------------------------------------------------------------------------------------------

#
#Copyright 2013, Janus Remote Communications
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions
#are met:
#
#Redistributions of source code must retain the above copyright notice,
#this list of conditions and the following disclaimer.
#
#Redistributions in binary form must reproduce the above copyright
#notice, this list of conditions and the following disclaimer in
#the documentation and/or other materials provided with the distribution.
#
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS``AS
#IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import serial
import time

import traceback
import syslog

class ser:

    mySer = -1

    def __init__(self, dev, speed, format):

        self.mySer = serial.Serial()    
        self.set_speed(dev, speed, format)
        self.flushInput()

    def __del__(self):

        self.mySer.close()

    def send(self, string):

        #Write a string to output buffer        
        return self.mySer.write(string)

    def sendbyte(self, byte):

        #Write a byte to output buffer
        return self.mySer.write(chr(byte))

    def receive(self, timeOut):

        try:
            #Start timeout counter
            start = time.time()
            timeout = int(timeOut)   

            while self.mySer.inWaiting() == 0:
                if (time.time() - start > timeout):
                    return ''

        except:
            pass
            
        return self.mySer.read() 

    def receivebyte(self, timeOut):

        #Read in a byte from input buffer
        #Timeout if no byte to read

        try:
            #Start timeout counter
            start = time.time()
            timeout = int(timeOut)   

            while self.mySer.inWaiting() == 0:
                if (time.time() - start > timeout):
                    return ''

        except:
            pass

        return self.mySer.read(1)
        
    def read(self):

        #Read in all characters from input buffer
        #Exit if no characters to read

        if self.mySer.inWaiting() == 0:
            return '' 
            
        return self.mySer.read()
            
    def readbyte(self):

        #Read in a byte from input buffer
        #Exit if no byte to read

        if self.mySer.inWaiting() == 0:
            return '' 
        
        return self.mySer.read(1)

    def flushInput(self):

        return self.mySer.flushInput()

    def setDCD(self, dcd):
            
        if dcd == 0:
            print 'dummy setDCD(0)'
        else:
            print 'dummy setDCD(1)'
        
        return

    def setCTS(self, cts):

        return self.mySer.setRTS(cts)  # CTS on the PC is connected instead of CTS...

    def setDSR(self, dsr):

        return self.mySer.setDTR(dsr)  # DTR on the PC is connected instead of DSR...

    def setRI(self, ri):

        if ri == 0:
            print 'dummy setRI(0)'
        else:
            print 'dummy setRI(1)'
        
        return

    def getRTS(self):

        return self.mySer.getCTS()

    def getDTR(self):

        return self.mySer.getDSR()
    
    def set_speed(self, dev, speed, format):

        if self.mySer.isOpen():
            self.mySer.close() 

        if speed == '300':
            self.mySer.baudrate = 300
        elif speed == '600':
            self.mySer.baudrate = 600
        elif speed == '1200':
            self.mySer.baudrate = 1200
        elif speed == '2400':
            self.mySer.baudrate = 2400
        elif speed == '4800':
            self.mySer.baudrate = 4800
        elif speed == '9600':
            self.mySer.baudrate = 9600
        elif speed == '19200':
            self.mySer.baudrate = 19200
        elif speed == '38400':
            self.mySer.baudrate = 38400
        elif speed == '57600':
            self.mySer.baudrate = 57600
        elif speed == '115200':
            self.mySer.baudrate = 115200
        else:
            return
            
        if format == '8N1':
            self.mySer.bytesize = serial.EIGHTBITS
            self.mySer.parity = serial.PARITY_NONE
            self.mySer.stopbits = serial.STOPBITS_ONE
        elif format == '8N2':
            self.mySer.bytesize = serial.EIGHTBITS
            self.mySer.parity = serial.PARITY_NONE
            self.mySer.stopbits = serial.STOPBITS_TWO
        elif format == '8E1':
            self.mySer.bytesize = serial.EIGHTBITS
            self.mySer.parity = serial.PARITY_EVEN
            self.mySer.stopbits = serial.STOPBITS_ONE
        elif format == '8O1':
            self.mySer.bytesize = serial.EIGHTBITS
            self.mySer.parity = serial.PARITY_ODD
            self.mySer.stopbits = serial.STOPBITS_ONE
        elif format == '7N1':
            self.mySer.bytesize = serial.SEVENBITS
            self.mySer.parity = serial.PARITY_NONE
            self.mySer.stopbits = serial.STOPBITS_ONE
        elif format == '7N2':
            self.mySer.bytesize = serial.SEVENBITS
            self.mySer.parity = serial.PARITY_NONE
            self.mySer.stopbits = serial.STOPBITS_TWO
        elif format == '7E1':
            self.mySer.bytesize = serial.SEVENBITS
            self.mySer.parity = serial.PARITY_EVEN
            self.mySer.stopbits = serial.STOPBITS_ONE
        elif format == '7O1':
            self.mySer.bytesize = serial.SEVENBITS
            self.mySer.parity = serial.PARITY_ODD
            self.mySer.stopbits = serial.STOPBITS_ONE
        elif format == '8E2':
            self.mySer.bytesize = serial.EIGHTBITS
            self.mySer.parity = serial.PARITY_EVEN
            self.mySer.stopbits = serial.STOPBITS_TWO
        else:
            return
        
        if dev == 'ttyS0':
            self.mySer.port = '/dev/ttyS0'
        elif dev == 'ttyS1':
            self.mySer.port = '/dev/ttyS1'
        elif dev == 'ttyS2':
            self.mySer.port = '/dev/ttyS2'
        elif dev == 'ttyS3':
            self.mySer.port = '/dev/ttyS3'
            self.mySer.rtscts = True
        elif dev == 'ttyS4':
            self.mySer.port = '/dev/ttyS4'
        elif dev == 'ttyUSB0':
            self.mySer.port = '/dev/ttyUSB0'
        elif dev == 'ttyUSB2':
            self.mySer.port = '/dev/ttyUSB2'
        elif dev == 'ttyACM0':
            self.mySer.port = '/dev/ttyACM0'
        else:
            return

        return self.mySer.open()
