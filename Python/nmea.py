##------------------------------------------------------------------------------------------------------------------
## Module: nmea.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 06/29/2012)    :    Initial release
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

import traceback
import syslog

def getNextSentence (inSTR1):

    # Method inputs:
    #    inSTR$:
    #       Any valid NMEA $GP sentence
    #   timeOut:
    #       1 to 10 = Select all NMEA sentences

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data
    #    2:    NMEA Command Syntax error
    #    3:    NMEA Command Checksum error
    #    4:    Unhandled command

    #Example sentences
    #$GPGLL,4147.8978,N,08816.2419,W,141857.00,A,A*74                                
    #$GPGSA,A,3,02,04,05,10,12,13,17,23,25,,,,1.6,1.0,1.3*35                         
    #$GPGSV,3,1,12,12,52,246,29,05,48,189,23,23,06,035,34,04,42,061,34*7B            
    #$GPGSV,3,2,12,02,75,005,24,17,07,120,22,29,11,304,23,10,56,070,37*76            
    #$GPGSV,3,3,12,13,14,061,29,25,37,295,22,51,37,207,,48,24,236,*74                
    #$GPRMC,141858.000,A,4147.8978,N,08816.2419,W,0.0,253.2,260112,,,A*7C            
    #$GPGGA,141858.000,4147.8978,N,08816.2419,W,1,09,1.0,219.9,M,-43.5,M,,0000*6A    
    #$GPVTG,253.2,T,,M,0.0,N,0.0,K,A*0B                                              
    #$GPZDA,141858.000,26,01,2012,00,00*53

    #Encountered errors:
    #$GPGSV,3,3,12$GPGLL,4147.9000,N,08816.2067,W,170021.00,A,A*75

    try:
        
        lenght = len(inSTR1)
        
        #find NMEA sentence start position
        pos1 = inSTR1.find('$',0,lenght)
        if (pos1 == -1):
            #complete NMEA sentence not found
            rtnList[0] = 0
            return rtnList
        
        #find NMEA sentence stop position
        pos2 = inSTR1.find('\r\n',pos1,lenght)
        if (pos2 == -1):
            #complete NMEA sentence not found
            rtnList[0] = 0
            return rtnList
        
        #look for leading partial sentence
        pos1 = inSTR1.rfind('$',0,pos2)
        
        sentence = inSTR1[pos1:pos2 +2]
        
        if ((inSTR1[pos1:pos1+6] == '$GPGLL') or (inSTR1[pos1:pos1+6] == '$GPGSA') or (inSTR1[pos1:pos1+6] == '$GPRMC') or (inSTR1[pos1:pos1+6] == '$GPGGA') or (inSTR1[pos1:pos1+6] == '$GPVTG') or (inSTR1[pos1:pos1+6] == '$GPZDA') or (inSTR1[pos1:pos1+6] == '$GPGSV')):
            
            res = testChecksum (sentence)
            if (res[0] == 0):
                #print 'Found NMEA Sentence --> Check passed\r\n'
                rtnList[0] = 1
                rtnList[1] = sentence
                return rtnList
            elif (res[0] == 3):
                rtnList[0] = 3
                rtnList[1] = sentence
                return rtnList
            else:
                rtnList[0] = res[0]
                rtnList[1] = sentence
                return rtnList

        else:
            #Unhandled command
            rtnList[0] = 4
            rtnList[1] = sentence
            return rtnList

    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

    return rtnList

def testChecksum (inSTR1):

    rtnList = [-1,-1]
    # [return status,return data]
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data
    #    2:    NMEA Command Syntax error
    #    3:    NMEA Command Checksum error

    try:

        
        tmpList = inSTR1.split('*')
        if (len(tmpList) != 2):
            rtnList[0] = 2
            return rtnList

        tmpSTR1 = tmpList[0]
        tmpSTR1 = tmpSTR1[1:len(tmpSTR1)]
        tmpSTR2 = tmpList[1].strip()
                
        Checksum = 0
        for x in tmpSTR1:           
            Checksum = Checksum ^ ord(x)

        tmpSTR3 = str(hex(Checksum))[2:4].upper()            
        if len(tmpSTR3) != 2:
            tmpSTR3 = '0' + tmpSTR3  
        
        if (tmpSTR2 != tmpSTR3):
            rtnList[0] = 3
            return rtnList
            
        rtnList[0] = 0

    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

    return rtnList