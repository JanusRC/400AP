#!/usr/bin/python

##------------------------------------------------------------------------------------------------------------------
## Module: demoGps.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 06/29/2012)    :    Initial release
##    V1.1.0    (Thomas W. Heck, 11/12/2012)    :    Replaced timeout code, with method
##                                                   using time module  
##    V2.0.0    (Thomas W. Heck, 01/11/2013)    :    Code cleanup
##    V2.0.1    (Thomas W. Heck, 01/17/2013)    :    Added delay before powering on Plug-in Terminus, allows
##                                                   PWRMON to drop after UART set to high-Z and VBUS disabled
##    V2.1.0    (Thomas W. Heck, 01/29/2013)    :    Demo Release V2.1, added code for Online Mode, cleaned up
##                                                   output messages
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

def get_pids(process_name):
    ## TWH, 11/13/2012:  Recoded to return a list of pids, return list without whitespace characters
    return subprocess.check_output('pidof ' + str(process_name),shell=True).rstrip().split(' ')  

def ppp_cleanup():

    try:

        try:
            #kill all running pppd processes
            while(1):
                pids = get_pids('pppd')         
                os.kill(int(pids[0]),9)
                #print 'Process killed {' + str(pid[0]) + '}'
        except subprocess.CalledProcessError, e:
            #print 'No PPP process running: ' + str(e)
            pass
        except:
            #print syslog.LOG_ERR, traceback.format_exc()
            syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
            return -1    

        #Delete ppp0.pid if exists
        subprocess.check_output('rm -f /var/run/ppp0.pid',shell=True)

        #Remove Lock if exists
        subprocess.check_output('rm -f /var/lock/LCK..ttyS1',shell=True)
        subprocess.check_output('rm -f /var/lock/LCK..ttyACM0',shell=True)
        subprocess.check_output('rm -f /var/lock/LCK..ttyUSB0',shell=True)

    except:
        #print syslog.LOG_ERR, traceback.format_exc()
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
        return -1

    return 0

def main():

    returnVal = -1
    # return status:
    #   -1:    Un-handled Exception occurred
    #    0:    Method exited without error
    #    1:    Error occurred

    try:

        # Configuration checks
        if (myApp.CGMM == 'GE865'):            
            myApp.GPS_PORT = 'ttyS4'
            myApp.GPS_BAUD = '9600'
            myApp.GPS_FORMAT = '8N1'
        elif (myApp.CGMM == 'HE910'):
            myApp.GPS_PORT = 'ttyACM0'
            myApp.GPS_BAUD = '115200'
            myApp.GPS_FORMAT = '8N1'
        elif (myApp.CGMM == 'CC864-DUAL'):
            myApp.GPS_PORT = 'ttyUSB2'
            myApp.GPS_BAUD = '115200'
            myApp.GPS_FORMAT = '8N1'
        else:
            print 'Demo is configured with an unknown cellular device model, CGMM=' + myApp.CGMM
            raise UserWarning

        rtnList = myGPIO.initIO ()
        if rtnList[0] == -1: raise UserWarning

        #Inhibit VBUS voltage
        rtnList = myGPIO.setEnableVbus(0)
        if rtnList[0] == -1: raise UserWarning

        #High-Z all UART pins driving into Plug-in Terminus
        rtnList = myGPIO.setUartEnable(1)
        if rtnList[0] == -1: raise UserWarning

        #Give the USB host some time to disconnect radio
        time.sleep(4)

        rtnList = myGPIO.setPoweredState(1,15)  
        if rtnList[0] == -1 or rtnList[0] == -2: raise UserWarning

        #Enable UART I/O
        rtnList = myGPIO.setUartEnable(0)
        if rtnList[0] == -1: raise UserWarning

        #Power VBUS input
        rtnList = myGPIO.setEnableVbus (1)
        if rtnList[0] == -1: raise UserWarning


        #Wait for module to turn on
        start = time.time()
        timeout = 60

        print 'SIM Verification Cycle'
        rtnList = ATC.sendAtCmd('AT+CPBS?',ATC.properties.CMD_TERMINATOR,1)
        if (rtnList[0] == -1): raise UserWarning

        if rtnList[1].find("+CPBS")<0:
            print 'SIM busy! ....waiting!\n'

        while rtnList[1].find("+CPBS:")< 0 :
            rtnList = ATC.sendAtCmd('AT+CPBS?',ATC.properties.CMD_TERMINATOR,1)
            if (rtnList[0] == -1): raise UserWarning
            if (time.time() - start > timeout):
                print 'Check if SIM card is installed'
                syslog.syslog('Check if SIM card is installed')
                raise UserWarning
            time.sleep(1)

        print 'SIM ready'

        #Check if cellular device model identification code matches configuration file        
        rtnList = ATC.sendAtCmd('AT+CGMM',ATC.properties.CMD_TERMINATOR,5)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or (rtnList[0] == 0) or rtnList[1] == "ERROR": raise UserWarning
        if rtnList[0] == 1:
            if (myApp.CGMM != rtnList[1]):
                syslog.syslog('demo400ap.conf file defines CGMM=' + myApp.CGMM + ', but 400AP has ' + rtnList[1] + ' installed.')
                syslog.syslog('Please correct the demo400ap.conf file and re-run script!')
                print 'demo400ap.conf file defines CGMM=' + myApp.CGMM + ', but 400AP has ' + rtnList[1] + ' installed.'
                print 'Please correct the demo400ap.conf file and re-run script!'
                raise UserWarning

        # Configuration specific AT Command setup
        if (myApp.CGMM == 'GE865'):
            #GSM 2.5G
            #GSM865CF

            #Scan /sys and populate /dev
            res = subprocess.call('mdev -s', shell=True)

            #Record IMEI        
            rtnList = ATC.sendAtCmd('AT+CGSN',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or (rtnList[0] == 0) or rtnList[1] == "ERROR": raise UserWarning
            if rtnList[0] == 1:
                myApp.IMEI_MEID = rtnList[1]

        elif (myApp.CGMM == 'HE910'):

            #HSPA 3G
            #HSPA910CF

            #load ACM driver            
            res = subprocess.call('modprobe cdc-acm', shell=True)
            #Scan /sys and populate /dev
            res = subprocess.call('mdev -s', shell=True)

            #Wait for USB devices to populate /dev
            time.sleep(2)

            #Record IMEI        
            rtnList = ATC.sendAtCmd('AT+CGSN',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or (rtnList[0] == 0) or rtnList[1] == "ERROR": raise UserWarning
            if rtnList[0] == 1:
                myApp.IMEI_MEID = rtnList[1]

            #Set SLED to indicate radio status        
            rtnList = ATC.sendAtCmd('AT#GPIO=1,0,2',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or (rtnList[0] == 0) or rtnList[1] == "ERROR": raise UserWarning        
            rtnList = ATC.sendAtCmd('AT#SLED=2',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or (rtnList[0] == 0) or rtnList[1] == "ERROR": raise UserWarning
            rtnList = ATC.sendAtCmd('AT#SLEDSAV',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or (rtnList[0] == 0) or rtnList[1] == "ERROR": raise UserWarning

        elif (myApp.CGMM == 'CC864-DUAL'):

            #CDMA 2.5G
            #CDMA864CF

            #load option driver
            res = subprocess.call('modprobe option', shell=True)
            #Scan /sys and populate /dev
            res = subprocess.call('mdev -s', shell=True)
            
            #Wait for USB devices to populate /dev
            time.sleep(2)

            #Future check to determine if the CDMA radio is provisioned

            #Record MEID        
            rtnList = ATC.sendAtCmd('AT#MEID?',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or (rtnList[0] == 0) or rtnList[1] == "ERROR": raise UserWarning
            if rtnList[0] == 1:
                myApp.IMEI_MEID = rtnList[1].replace(',','')

            #Disable GPS
            rtnList = ATC.sendAtCmd('AT$GPSP=0',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning
            
            #Select GPS Path
            rtnList = ATC.sendAtCmd('AT$GPSPATH=1',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning
            
            #Select GPS Antenna Type
            rtnList = ATC.sendAtCmd('AT$GPSAT=1',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning
            
            #Choose ttyUSB2 mode
            rtnList = ATC.sendAtCmd('AT$GPSPORT=NMEA',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning
            #Choose Enable ALL NMEA sentences
            rtnList = ATC.sendAtCmd('AT$GPSNMUN=2,1,1,1,1,1',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning
            #Enable GPS
            rtnList = ATC.sendAtCmd('AT$GPSP=1',ATC.properties.CMD_TERMINATOR,5)
            if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning


        #print myApp.GPS_PORT,myApp.GPS_BAUD,myApp.GPS_FORMAT,myApp.CGMM
        
        gps = GpsPoller(myApp.GPS_PORT,myApp.GPS_BAUD,myApp.GPS_FORMAT,myApp.CGMM)
        gps.start()

        #Set Network specific settings
        rtnList = NETWORK.initNetwork(myApp.CGMM,myApp.ENS)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

        #Initialize SOCKET communications
        rtnList = SOCKET_400AP.init(myApp.CGMM,'1',myApp.APN)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

        #Wait for Network registration
        rtnList = NETWORK.isRegistered(180)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

        #Wait for Network registration
        rtnList = NETWORK.isDataAttached(myApp.CGMM,180)
        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

        print ''

        # Loop forever, without this loop the script would run once and exit script mode.  On reboot or power-on the script would run once more
        while True:

            #Start timeout counter
            start = time.time()
            timeout = int(myApp.INTERVAL)  

            while True:

                #If interval timer expires then send packet to server       
                if (time.time() - start > timeout):

                    #Poll NMEA GPGSA Sentence loop until GPS fix available
                    GPGSA = gps.get_current_GPGSA()
                    if GPGSA.split(',')[2] == '1':
                        print ''
                        print 'Waiting for GPS position fix.'
                        print 'Please place antenna in a location with a clear sky view.'
                        print 'On a cold start when the GPS receiver has no Almanac or Ephemeris data, position fix might take a long time.'
                        print 'If position fix is taking longer than 10 minutes indoors try a window with a different view of the sky.'
                        print 'Worst case you will need to get the antenna outdoors with a clear sky view.'

                        #exitLoop = '1'
                        fixCounter = 0
                        #while(exitLoop == '1'):
                        while(1):
                            GPGSA = gps.get_current_GPGSA()
                            fixCounter = fixCounter + 1
                            print GPGSA + 'Elapse time: %5d seconds' %fixCounter
                            time.sleep(1)
                            if GPGSA.split(',')[2] != '1':
                                break
                            sys.stdout.write('\033[A\033[2K\033[A\033[2K')

                        print 'GPS receiver has calculated a position fix.\r\n'

                    print 'Opening Connection to server: ' + myApp.IP + ':' + myApp.PORT + '\r\n'

                    #Fix for 09.01.024 Firmware
                    if (myApp.CGMR == '09.01.024') or (myApp.CGMR == '09.01.023-B021') :
                        connMode = '0'
                    else:
                        connMode = '1'

                    #Connect to server
                    #Pass in: IP Address, IP Port, sockNum, GPRSuserName, GPRSuserPassword,Connection Mode
                    rtnList = SOCKET_400AP.openSocket(myApp.IP,myApp.PORT,'1','','',myApp.PROTOCOL,connMode)
                    if (rtnList[0] == -1) or (rtnList[0] == -2) : raise UserWarning

                    #If socket open upload data
                    if rtnList[1] == 'OK':
                        ##Socket has been opened in connMode = 1 "command mode connection"
                        ## Please refer to AT#SD command in Telit AT Command Guide 

                        #illuminate Green LED
                        res = myGPIO.setGrnLed(1)
                        if res[0] == -1: raise UserWarning

                        print 'Connection opened (Command Mode)' + '\r\n'
                        
                        GPGGA = gps.get_current_GPGGA()
                        connMode = 0
                        #Build String to send to customer server            
                        STR1 = myApp.IMEI_MEID +',' + GPGGA

                        print 'Sending Data: ' + STR1 + '\r\n'

                        #Send STR1 to server
                        rtnList = SOCKET_400AP.send_CM(STR1,1,180)                         
                        if (rtnList[0] == -1): raise UserWarning
                        if (rtnList[0] == -2):
                            syslog.syslog(syslog.LOG_ERR, 'send_CM: Timeout')
                            ##!!!!!!!!!!!!!!!!!   what to do here    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11
                            break

                        print 'Data Sent' + '\r\n'

                        #Close Socket
                        rtnList = SOCKET_400AP.closeSocket('1')
                        if (rtnList[0] == -1) or (rtnList[0] == -2) : raise UserWarning

                        print 'Connection Closed' + '\r\n'

                        #turn off Green LED
                        res = myGPIO.setGrnLed(0)
                        if res[0] == -1: raise UserWarning

                        break

                    elif rtnList[1] == 'CONNECT':
                        ##Socket has been opened in connMode = 0 "online mode connection"
                        ## Please refer to AT#SD command in Telit AT Command Guide

                        #illuminate Green LED
                        res = myGPIO.setGrnLed(1)
                        if res[0] == -1: raise UserWarning

                        print 'Connection opened (Online Mode)' + '\r\n'

                        GPGGA = gps.get_current_GPGGA()

                        #Build String to send to customer server            
                        STR1 = myApp.IMEI_MEID +',' + GPGGA

                        print 'Sending Data: ' + STR1 + '\r\n'

                        rtnList = SOCKET_400AP.send_OM(STR1)
                        if (rtnList[0] == -1): raise UserWarning

                        print 'Data Sent' + '\r\n'

                        # Break out of Data Mode
                        rtnList = SOCKET_400AP.exitDataMode(20)
                        if (rtnList[0] == -1): raise UserWarning

                        print 'Exited Data Mode' + '\r\n'

                        #Close Socket
                        rtnList = SOCKET_400AP.closeSocket('1')
                        if (rtnList[0] == -1) or (rtnList[0] == -2) : raise UserWarning

                        print 'Connection Closed' + '\r\n'

                        #turn off Green LED
                        res = myGPIO.setGrnLed(0)
                        if res[0] == -1: raise UserWarning

                        break

                    else:

                        print "Connection failed to open" + "\r\n"                            

                        #What is the signal strength?
                        rtnList = ATC.sendAtCmd('AT+CSQ',ATC.properties.CMD_TERMINATOR,5)
                        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                        print "Signal Strength (AT+CSQ): " + rtnList[1] + "\r\n"

                        # Is Plug-in Terminus connected to Network?                                                                        
                        rtnList = NETWORK.isRegistered(1)
                        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                        if (rtnList[0] == 0):
                            print "Plug-in Terminus is registered on network" + "\r\n"
                        else:
                            print "Plug-in Terminus is NOT registered on network" + "\r\n"

                        #Is a PDP context activated?
                        rtnList = ATC.sendAtCmd('AT#SGACT?',ATC.properties.CMD_TERMINATOR,20)
                        if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                        print "PDP Context status (AT#SGACT?): " + rtnList[1] + "\r\n"

                        # Is Plug-in Terminus attached to Data service?
                        rtnList = NETWORK.isDataAttached(myApp.CGMM,1)
                        if (rtnList[0] == -1) or (rtnList[0] == -2) : raise UserWarning
                        if (rtnList[0] == 0):
                            print "Plug-in Terminus is attached to Data service" + "\r\n"
                        else:
                            print "Plug-in Terminus is NOT attached to Data service"

                        break
                else:
                    print "Next position update to server in: %6d Seconds\r" % (int(myApp.INTERVAL) - (time.time() - start))
                    
                    #print "Next position update to server in: " + str(int(myApp.INTERVAL) - (time.time() - start)) + " Seconds" + "\r"
                    time.sleep(1)
                    sys.stdout.write('\033[A\033[2K')


    except UserWarning:
        print 'Script exit with warning!'
        syslog.syslog('Script exit with warning!')
        returnVal = 1
    except Exception:
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
        print syslog.LOG_ERR, traceback.format_exc()
        returnVal = -1
    finally:        
        gps.stop()

    gps.stop()

    return returnVal

try:

    import syslog
    import traceback
    import sys
    import subprocess
    import os
    import time
    
    from GpsPoller import *

    syslog.syslog('400AP GPS demo script started')

    #Kill running pppd processes   
    res = ppp_cleanup()
    if res == -1: raise UserWarning    

    import ATC_400AP as ATC

    ##Serial port was opened need to check if we can continue

    import NETWORK_400AP as NETWORK
    import SOCKET_400AP

    import configuration
    #Get configuration from demo400ap.conf file
    myApp = configuration.conf('/opt/demo400ap','demo400ap.conf') 

    if myApp.CONF_STATUS != 0:
        syslog.syslog('demo400ap configuration error: ' + str(myApp.CONF_STATUS)) 
        raise UserWarning

    import GPIO_400AP
    myGPIO = GPIO_400AP.gpio(myApp.PRODUCTION, myApp.CGMM)
    
    if __name__ == "__main__":
        #print 'main() running'
        res = main()
        os._exit(int(res))
        
except UserWarning:
    #print 'Script exit with warning!'
    syslog.syslog('Script exit with warning!')
    os._exit(1)
    
except:
    #print syslog.LOG_ERR, traceback.format_exc()
    syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    os._exit(-1)

