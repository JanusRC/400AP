#!/usr/bin/python

##------------------------------------------------------------------------------------------------------------------
## Module: GpsPoller.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 06/29/2012)    :    Initial release
##    V1.1.0    (Thomas W. Heck, 11/12/2012)    :    Replaced timeout code, with method
##                                                   using time module
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


import threading
import traceback
import syslog
import time

import SER_400AP
import nmea

#import pdb
# pdb.set_trace()

class GpsPoller(threading.Thread):
    
    def __init__(self,PORT,BAUD,FORMAT,RADIO):
    #Constructor
        threading.Thread.__init__(self)
        self.GPS_UART = SER_400AP.ser(PORT, BAUD, FORMAT)
        self.current_GPGLL = ''
        self.current_GPGSA = ''
        self.current_GPGSV = ''
        self.current_GPRMC = ''
        self.current_GPGGA = ''
        self.current_GPVTG = ''
        self.current_GPZDA = ''
        self.NMEA_BUFFER = ''
        self.CGMM = RADIO
        self.stop_flag = True
        syslog.syslog('GpsPoller.py initialized')

    def get_current_GPGLL(self):
        #print self.current_GPGLL
        return self.current_GPGLL
    
    def get_current_GPGSA(self):
        #print self.current_GPGSA
        return self.current_GPGSA

    def get_current_GPGSV(self):
        #print self.current_GPGSV
        return self.current_GPGSV    

    def get_current_GPRMC(self):
        #print self.current_GPRMC
        return self.current_GPRMC
    
    def get_current_GPGGA(self):
        #print self.current_GPGGA
        return self.current_GPGGA

    def get_current_GPVTG(self):
        #print self.current_GPVTG
        return self.current_GPVTG
    
    def get_current_GPZDA(self):
        #print self.current_GPZDA
        return self.current_GPZDA

    def run(self):
        try:

            # make sure only one instance runs
            if self.stop_flag == False: return
            else: self.stop_flag = False
            
            if (self.CGMM == 'HE910'):
                #Disable GPS
                rtnList = self.sendAtCmd('AT$GPSP?','OK\r\n',5)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR":
                    #AT Command error
                    syslog.syslog('GpsPoller.py -> AT Command failed -> ' + str(rtnList[1]))
                    self.stop_flag = True
                    syslog.syslog('GpsPoller.py thread stopped')
                    return
                if (rtnList[1] == "$GPSP: 0"):
                    #Enable GPS
                    rtnList = self.sendAtCmd('AT$GPSP=1','OK\r\n',5)
                    if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR":
                        #AT Command error
                        syslog.syslog('GpsPoller.py -> AT Command failed -> ' + str(rtnList[1]))
                        self.stop_flag = True
                        syslog.syslog('GpsPoller.py thread stopped')
                        return
                
                #Choose Enable ALL NMEA sentences
                rtnList = self.sendAtCmd('AT$GPSNMUN=3,1,1,1,1,1,1','CONNECT\r\n',5)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR":
                    #AT Command error
                    syslog.syslog('GpsPoller.py -> AT Command failed -> ' + str(rtnList[1]))
                    self.stop_flag = True
                    syslog.syslog('GpsPoller.py thread stopped')
                    return
                
            syslog.syslog('GpsPoller.py thread running')
            
            while not(self.stop_flag):

                #read serial nmea stream
                tempSTR = str(self.GPS_UART.read())
                self.NMEA_BUFFER += tempSTR
                #print tempSTR

                #parse out complete NMEA strings
                res = nmea.getNextSentence(self.NMEA_BUFFER)
                if (res[0] == 0):
                    #No NMEA sentence found
                    pass
                elif ((res[0] == 1) or (res[0] == 2) or (res[0] == 3) or (res[0] == 4)):
                    #print str(res[0])
                    #print str(res[1])

                    #strip sentence off nmea buffer
                    pos1 = self.NMEA_BUFFER.find(res[1],0,len(self.NMEA_BUFFER))
                    lenght  = len(res[1])
                    pos2 = pos1 + lenght
                    self.NMEA_BUFFER = self.NMEA_BUFFER[pos2:len(self.NMEA_BUFFER)]

                    if (res[0] == 1):
                        #save current NMEA sentence
                        if (res[1].find('$GPGLL') >= 0 ):
                            self.current_GPGLL = res[1]
                        elif(res[1].find('$GPGSA') >= 0 ):
                            self.current_GPGSA = res[1]
                        elif(res[1].find('$GPGSV') >= 0 ):
                            #append all GPGSV sentences together
                            tmpList = res[1].split(',')
                            if tmpList[2] == '1':
                                self.current_GPGSV = res[1]
                            else:
                                self.current_GPGSV += res[1]
                        elif(res[1].find('$GPRMC') >= 0 ):
                            self.current_GPRMC = res[1]
                        elif(res[1].find('$GPGGA') >= 0 ):
                            self.current_GPGGA = res[1]
                        elif(res[1].find('$GPVTG') >= 0 ):
                            self.current_GPVTG = res[1]        
                        elif(res[1].find('$GPZDA') >= 0 ):
                            self.current_GPZDA = res[1]
                    elif (res[0] == 2):
                        syslog.syslog('GpsPoller.py -> Syntax error:  ' + str(res[1]))
                    elif (res[0] == 3):
                        syslog.syslog('GpsPoller.py -> Checksum error:  ' + str(res[1]))
                    elif (res[0] == 4):
                        syslog.syslog('GpsPoller.py -> Unhandled NMEA command:  ' + str(res[1]))
                    
                else:
                    #unhandled return value
                    syslog.syslog('GpsPoller.py -> Unhandled return value: nmea.getNextSentence = ' + str(res[0]))
                    self.stop_flag = True
                    break

        except:
            syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
        finally:
            self.stop_flag = True
        
        syslog.syslog('GpsPoller.py thread stopped')
        
    def stop(self):
        self.stop_flag = True
        return
    
    ################################################################################################
    ## Methods for sending and receiving AT Commands
    ################################################################################################
    def sendAtCmd(self, theCommand, theTerminator, timeOut):
    # This function sends an AT command to the MDM interface
    
        # Input Parameter Definitions
        #   theCommand: The AT command to send to MDM interface
        #   theTerminator: string or character at the end of AT Command 
        #   timeOut: number of [1/10 seconds] command could take to respond
    
        try:
    
            rtnList = [-1,-1]    #[return status,return data]
            # return status:
            #   -2:    Timeout
            #   -1:    Exception occurred
            #    0:    No errors occurred, no return data
            #    1:    No errors occurred, return data
    
    
            #Clear input buffer
            rtnList[1] = 'junk'
            while(rtnList[1] != ''):
                rtnList[1] = self.GPS_UART.read()
    
            print 'Sending AT Command: ' + theCommand + "\r\n"
            rtnList[1] = self.GPS_UART.send(theCommand)
            rtnList[1] = self.GPS_UART.sendbyte(0x0d)
    
            while True:
                #Wait for AT command response
                rtnList = self.mdmResponse(theTerminator, timeOut)
                if (rtnList[0] == -1) or (rtnList[0] == -2) : return rtnList
                elif rtnList[0] == 1:
                    #what happens if res doesn't return data?
                    #Did AT command respond without error?
                    pos1 = rtnList[1].rfind('ERROR',0,len(rtnList[1]))    
                    pos2 = rtnList[1].rfind(theTerminator,0,len(rtnList[1]))
                    if ((pos1 != -1) or (pos2 != -1)) :
                        rtnList = self.parseResponse(rtnList[1])
                        if rtnList[0] == -1: return rtnList
                        elif rtnList[0] == 1:
                            #what happens if res doesn't return data?
                            rtnList[0] = 1
                            break
    
        except:
            rtnList[0] = -1
            syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        print rtnList[1]
    
        return rtnList
    
    def mdmResponse(self, theTerminator, timeOut):
    # This function waits for AT Command response and handles errors and ignores unsolicited responses
    
    # Input Parameter Definitions
    #   theTerminator: string or character at the end of a received string which indicates end of a response
    #   timeOut: number of seconds command could take to respond
    
        try:
    
            rtnList = [-1,-1]    #[return status,return data]
            # return status:
            #   -2:    Timeout
            #   -1:    Exception occurred
            #    0:    No errors occurred, no return data
            #    1:    No errors occurred, return data
    
            print 'Waiting for AT Command Response' + "\r\n"
    
            #Start timeout counter
            start = time.time()
            timeout = int(timeOut)       
    
            #Wait for response
            rtnList[1] = ''
            while ((rtnList[1].find(theTerminator)<=-1) and (rtnList[1].find("ERROR")<=-1)):
                #MOD.watchdogReset()
                rtnList[1] += self.GPS_UART.read()
                
                if (time.time() - start > timeout):
                    rtnList[0] = -2
                    print "AT command timed out" + "\r\n"
                    return rtnList
                            
            rtnList[0] = 1

        except:
            rtnList[0] = -1
            syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return rtnList
    
    def parseResponse(self, inSTR):
    # This function parses out data return from AT commands
    
        # Input Parameter Definitions
        #   inSTR:  The response string from and AT command
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
    
            rtnList[1] = ''
            lenght = len(inSTR)
    
            if lenght != 0:
                pos1 = inSTR.find('ERROR',0,lenght)
                if (pos1 != -1):
                    rtnList[1] = 'ERROR'
                else:
                    list_in = inSTR.split( '\r\n' )
                    rtnList[1] = list_in[ 1 ]
    
            if len(rtnList[1]) > 0:
                rtnList[0] = 1
    
        except:
            rtnList[0] = -1
            syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return rtnList
