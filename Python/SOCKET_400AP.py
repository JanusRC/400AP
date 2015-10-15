##------------------------------------------------------------------------------------------------------------------
## Module: SOCKET_400AP.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 06/29/2012)    :    Initial release
##    V1.1.0    (Thomas W. Heck, 11/12/2012)    :    Replaced timeout code, with method
##                                                   using time module
##    V2.1.0    (Thomas W. Heck, 01/29/2013)    :    Demo Release V2.1, Added send_OM method to support sending data
##                                                   in Online Mode
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
import time

import ATC_400AP as ATC

class properties:
    CMD_BUFFER = ''

################################################################################################
## Methods for handling GPRS communication
################################################################################################

def init(CGMM,PDPindex,APN):

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:

        if (CGMM == 'GE865') or (CGMM == 'HE910') : 
            #Define GPRS Settings, MUST change APN String in script for your Carrier Specific setting
            rtnList = ATC.sendAtCmd('AT+CGDCONT=' + str(PDPindex) + ',"IP","' + str(APN) + '","0.0.0.0",0,0' ,ATC.properties.CMD_TERMINATOR,20)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList

        #How long does system wait before sending an under sized packet measured in 100ms settings
        rtnList = ATC.sendAtCmd('AT#DSTO=10' ,ATC.properties.CMD_TERMINATOR,20)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList
        
        #escape guard time, after set time escape sequence is accepted, set in 20ms settings
        rtnList = ATC.sendAtCmd('ATS12=40' ,ATC.properties.CMD_TERMINATOR,20)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList

        #disable the escape sequence from transmitting during a data session
        rtnList = ATC.sendAtCmd('AT#SKIPESC=1' ,ATC.properties.CMD_TERMINATOR,20)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList

        #Set connect timeOuts and packet sizes for PDP#1 and Socket#1
        rtnList = ATC.sendAtCmd('AT#SCFG=1,1,1500,600,100,10' ,ATC.properties.CMD_TERMINATOR,20)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList

        #Sets the behavior of #SSEND and #SREVC, Socket#1
        rtnList = ATC.sendAtCmd('AT#SCFGEXT=1,2,0,30,0,0' ,ATC.properties.CMD_TERMINATOR,20)

    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

    return rtnList

def openSocket(addr,port,sockNum,userID,userPassword,protocol,connMode):
    #Function Open a socket and responds with CONNECT, OK, NO CARRIER or ERROR

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:
        #Close Socket
        rtnList = ATC.sendAtCmd('AT#SS',ATC.properties.CMD_TERMINATOR,180)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList
        if (rtnList[1] !="#SS: 1,0"):
            rtnList = ATC.sendAtCmd('AT#SH=1',ATC.properties.CMD_TERMINATOR,180)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList
            
        #Activate PDP if needed  
        rtnList = ATC.sendAtCmd('AT#SGACT?',ATC.properties.CMD_TERMINATOR,180)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList
        if (rtnList[1] !="#SGACT: 1,1"):
            time.sleep(1)
            rtnList = ATC.sendAtCmd('AT#SGACT=1,1,"' + str(userID) + '","' + str(userPassword) + '"' ,ATC.properties.CMD_TERMINATOR,180) 
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList

        #Open Socket to Server in Data Mode
        if (str(protocol)=='TCP'):
            #TCP/IP requested
            #Test what connect method has been requested
            if connMode == '1':
                rtnList = ATC.sendAtCmd('AT#SD=1,0,' + str(port) + ',"' + str(addr) + '",0,0,' + str(connMode),ATC.properties.CMD_TERMINATOR,180)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList
            else:
                rtnList = ATC.sendAtCmd('AT#SD=1,0,' + str(port) + ',"' + str(addr) + '",0,0,' + str(connMode),'CONNECT\r\n',180)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList
            
        else:
            #UPD requested
            #Test what connect method has been requested
            if connMode == '1':
                rtnList = ATC.sendAtCmd('AT#SD=1,1,' + str(port) + ',"' + str(addr) + '",0,5559,' + str(connMode),ATC.properties.CMD_TERMINATOR,180)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList
            else:
                rtnList = ATC.sendAtCmd('AT#SD=1,1,' + str(port) + ',"' + str(addr) + '",0,5559,' + str(connMode),'CONNECT\r\n',180)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList
                
    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

    return rtnList

def send_CM(inSTR,connId,timeOut):

    #Send data during socket connection in Command Mode

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -2:    Timeout occurred
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    if (len(inSTR) == 0):
        rtnList[0] = 0
        return rtnList

    try:

        #Define GPRS Settings, MUST change APN String in script for your Carrier Specific setting
        rtnList = ATC.sendAtCmd('AT#SSEND=' + str(connId),'\r\n> ',180)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": return rtnList

        res = ATC.mySER.send(inSTR)
        res = ATC.mySER.sendbyte(0x1a)

        #Start timeout counter
        start = time.time()
        timeout = int(timeOut)  

        res = ''
        tmpByte = ''
        while True:
            tmpByte = ATC.mySER.readbyte()
            res += tmpByte

            if (res.find('\r\nOK\r\n')>=0):
                rtnList[0] = 0
                break
            if (time.time() - start > timeout):
                rtnList[0] = -2
                break

    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

    return rtnList

def send_OM(inSTR):

    #Send data during socket connection in Online Mode

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    if (len(inSTR) == 0):
        rtnList[0] = 0
        return rtnList

    try:

        res = ATC.mySER.send(inSTR)
        rtnList[0] = 0

    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

    return rtnList

def parseSRING():

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    syntaxFailed = 0

    pos1 = 0
    pos2 = 0
    pos3 = 0
    pos4 = 0
    pos5 = 0
    pos6 = 0
    lenData = 0
    sockNum = 0

    rtnList[1] = ''

    try:

        print properties.CMD_BUFFER

        # Has Data Arrived?
        pos1 = properties.CMD_BUFFER.find('SRING',0)
        if(pos1==-1):
            rtnList[0] = 1
            return rtnList
        
        pos2 = properties.CMD_BUFFER.find(':',pos1+1)            
        if(pos2==-1):
            rtnList[0] = 1
            return rtnList
        
        pos3 = properties.CMD_BUFFER.find(',',pos2+1)
        if(pos3==-1):
            rtnList[0] = 1
            return rtnList
        
        #Store reported Socket Number
        try:
            sockNum = int(properties.CMD_BUFFER[pos2+1:pos3],10)
        except:
            syntaxFailed = 1

        pos4 = properties.CMD_BUFFER.find(',',pos3+1)
        if(pos4==-1):
            rtnList[0] = 1
            return rtnList

        #Store reported Data length
        try:
            lenData = int(properties.CMD_BUFFER[pos3+1:pos4],10)
        except:
            syntaxFailed = 1
            
        pos5 = properties.CMD_BUFFER.find('\r\n',pos4+1)
        if(pos5==-1):
            rtnList[0] = 1
            return rtnList
        
        # Is valid Socket Number? (1 - 6)
        if ((sockNum<1) and (sockNum>6)):
            syntaxFailed = 1            

        if ((not(pos2>pos1)) and (not(pos2<pos3)) and (not(pos3<pos4)) and (not(pos4<pos5))):
            syntaxFailed = 1

        # Is Data size correct?
        if (lenData != (pos5 - (pos4+1))):
            syntaxFailed = 1
        
        if (syntaxFailed==0):
            #res = properties.CMD_BUFFER[pos4+1:pos5]
            # remove SRING: from buffer and leading characters
            properties.CMD_BUFFER = properties.CMD_BUFFER[pos5+2:len(properties.CMD_BUFFER)]        

        else:
            pos6 = properties.CMD_BUFFER.find('SRING:',pos1+1)
            if (pos6>-1):
                # remove SRING: from buffer and leading characters
                properties.CMD_BUFFER = properties.CMD_BUFFER[pos6:len(properties.CMD_BUFFER)]
            else:
                properties.CMD_BUFFER = properties.CMD_BUFFER[pos1+5:len(properties.CMD_BUFFER)]
    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
        rtnList[1] = ''

    return rtnList

def exitDataMode(timeOut):

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:
        #Exit data mode

        ##Lookup the Escape Sequence Guard Time
        ## Future Use
        
        # Delay to meet Escape Sequence Guard Time
        ## Remove Hard Coded Escape Sequence Guard Time
        time.sleep(1)

        #Start timeout counter
        start = time.time()

        ##Lookup the Escape Sequence
        ## Future Use
        
        #Sending +++
        ## Remove Hard Coded Escape Sequence
        rtnList[1] = ATC.mySER.send('+++')

        #Wait for response
        rtnList[1] = ''
        while rtnList[1].find("OK") <= -1:
            rtnList[1] += ATC.mySER.receive(1)
            if (time.time() - start > timeOut):
                rtnList[0] = -2
                return rtnList 

        rtnList[0] = 0

    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

    return rtnList

def closeSocket(sockNum):

    rtnList = [-1,-1]    #[return status,return data]
    # return status:
    #   -1:    Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    No errors occurred, return data

    try:
        #Close Socket
        rtnList = ATC.sendAtCmd('AT#SH=' + str(sockNum),ATC.properties.CMD_TERMINATOR,20)
    except:
        rtnList[0] = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())

    return rtnList
