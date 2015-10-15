#!/usr/bin/python

##------------------------------------------------------------------------------------------------------------------
## Module: demoPPP.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 06/29/2012)    :    Initial release
##    V1.1.0    (Thomas W. Heck, 11/12/2012)    :    Added connection testing
##    V1.1.1    (Thomas W. Heck, 11/13/2012)    :    Bug:    While attempting to determine
##                                                           if the script was already
##                                                           running, the script detected
##                                                           itself and exited.
##
##                                                   Fix:    Re-coded to check for multiple
##                                                           pid's.
##    V1.2.0    (Thomas W. Heck, 11/14/2012)    :    Added Start | Stop command line options
##    V1.3.0    (Thomas W. Heck, 11/21/2012)    :    Bug:    Serial port opened before
##                                                           checks for script already
##                                                           running, and pppd running
##                                                           checks.  Caused serial port
##                                                           to lock on a blocking read. 
##
##                                                   Fix:    Re-coded to check for script
##                                                           already running, and pppd
##                                                           running before opening serial
##                                                           port.  Future release will
##                                                           handle lock files.
##    V1.4.0    (Thomas W. Heck, 01/11/2013)    :    Remove locks on ttyUSB0 and ttyACM0
##                                                   Code cleanup
##    V1.4.1    (Thomas W. Heck, 01/17/2013)    :    Added delay before powering on Plug-in Terminus, allows
##                                                   PWRMON to drop after UART set to high-Z and VBUS disabled
##    V2.1.0    (Thomas W. Heck, 01/29/2013)    :    Demo Release V2.1
##------------------------------------------------------------------------------------------------------------------

##------------------------------------------------------------------------------------------------------------------
## Description:
## 
## This script starts or stops a PPP connection via the Cellular network via the Janus
## Plug-in Terminus embedded in the 400AP.  This is one way to handle a PPP connection
## with the 400AP and was created as an example.  It is recommend to execute this at 
## start-up via an S script in the /etc/init.d directory.  Your application can also  
## execute this script when needed.
##------------------------------------------------------------------------------------------------------------------

##------------------------------------------------------------------------------------------------------------------
## Notes:
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

def main(appArgv=''):

    returnVal = -1
    # return status:
    #   -1:    Un-handled Exception occurred
    #    0:    Method exited without error
    #    1:    Error occurred

    try:

        if appArgv == 'start':

            #Bring up ppp0 network interface

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


            #SIM status control - to avoid the 'SIM busy' error
            #The following sequence loops forever until SIM card is ready for use
            #
            #    Note: For GSM devices, will loop until a SIM card is installed
            #          or timeout occurs
            #

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
            if (myApp.CGMM == 'GE865') or (myApp.CGMM == 'HE910'):

                #GSM 2.5G - GSM865CF
                #or
                #HSPA 3G  - HSPA910CF

                if (myApp.CGMM == 'HE910'):

                    rtnList = myGPIO.setEnableVbus (1)
                    if rtnList[0] == -1: raise UserWarning
                    
                    #*****Caution: Magic Number need a better solution *****
                    time.sleep(2)

                    #load ACM driver            
                    res = subprocess.call('modprobe cdc-acm', shell=True)

                #Scan /sys and populate /dev
                res = subprocess.call('mdev -s', shell=True)

                #Disable Authentication
                rtnList = ATC.sendAtCmd('AT#GAUTH=0',ATC.properties.CMD_TERMINATOR,5)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or (rtnList[0] == 0) or rtnList[1] == "ERROR": raise UserWarning

                #Set Network specific settings
                rtnList = NETWORK.initNetwork(myApp.CGMM,myApp.ENS)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                #Initialize SOCKET communications
                rtnList = SOCKET_400AP.init(myApp.CGMM,'1',myApp.APN)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                #Wait for Network registration
                rtnList = NETWORK.isRegistered(120)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                #Wait for Network registration
                rtnList = NETWORK.isDataAttached(myApp.CGMM,120)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                if (myApp.CGMM == 'HE910'):
                    #Start ppp and create network interface ppp0
                    res = subprocess.call('pppd -d -detach /dev/ttyACM0 115200 file /etc/ppp/peers/modem_hspa910cf &', shell=True)
                else:
                    #Start ppp and create network interface ppp0
                    res = subprocess.call('pppd -d -detach /dev/ttyS1 115200 file /etc/ppp/peers/modem_gsm865cf &', shell=True)
                    
                
            elif (myApp.CGMM == 'CC864-DUAL'):

                #CDMA 2.5G
                #CDMA864CF

                rtnList = myGPIO.setEnableVbus (1)
                if rtnList[0] == -1: raise UserWarning

                #*****Caution: Magic Number need a better solution *****
                time.sleep(2)

                #load option driver
                res = subprocess.call('modprobe option', shell=True)
                #Scan /sys and populate /dev
                res = subprocess.call('mdev -s', shell=True)

                #Check if CDMA is provisioned for use on the network

                #Set Network specific settings
                rtnList = NETWORK.initNetwork(myApp.CGMM,myApp.ENS)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                #Initialize SOCKET communications
                rtnList = SOCKET_400AP.init(myApp.CGMM,'1',myApp.APN)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                #Wait for Network registration
                rtnList = NETWORK.isRegistered(120)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                #Wait for Network registration
                rtnList = NETWORK.isDataAttached(myApp.CGMM,120)
                if (rtnList[0] == -1) or (rtnList[0] == -2) or rtnList[1] == "ERROR": raise UserWarning

                #Start ppp and create network interface ppp0
                res = subprocess.call('pppd -d -detach file /etc/ppp/peers/modem_cdma864cf &', shell=True)

            returnVal = 0

        else:

            #Inhibit VBUS voltage
            rtnList = myGPIO.setEnableVbus(0)
            if rtnList[0] == -1: raise UserWarning
            #Give the USB host some time to disconnect radio
            time.sleep(4)
    
            #High-Z all UART pins driving into Plug-in Terminus
            rtnList = myGPIO.setUartEnable(1)
            if rtnList[0] == -1: raise UserWarning

            #Turn off Plug-in Terminus
            rtnList = myGPIO.setPoweredState(0,15)
            if rtnList[0] == -1: raise UserWarning
            
            #Test if radio turned off 
            if rtnList[0] == -2:
                #Power state change timed out, Force power-off, Initialize Radio I/0
                
                print 'Radio failed to turn off, Forcing power-down'
                
                #Disable Plug-in Terminus on-board regulator
                rtnList = myGPIO.setEnableSupply (1)
                if rtnList[0] == -1: raise UserWarning
                
                #RESET set to run state
                rtnList = myGPIO.setReset(0)
                if rtnList[0] == -1: raise UserWarning

                #ON_OFF set to run state
                rtnList = myGPIO.setOnOff(0)
                if rtnList[0] == -1: raise UserWarning

                #SERVICE set to run state
                rtnList = myGPIO.setService(0)
                if rtnList[0] == -1: raise UserWarning

                #GPS_RESET set to run state
                rtnList = myGPIO.setGpsReset(0)
                if rtnList[0] == -1: raise UserWarning

                #Inhibit VBUS voltage
                rtnList = myGPIO.setEnableVbus(0)
                if rtnList[0] == -1: raise UserWarning

                #High-Z all UART pins driving into Plug-in Terminus
                rtnList = myGPIO.setUartEnable(1)
                if rtnList[0] == -1: raise UserWarning
        
                #Enable Plug-in Terminus power supply
                rtnList = myGPIO.setEnableSupply(0)
                if rtnList[0] == -1: raise UserWarning

            returnVal = 0

    except UserWarning:
        print 'Script exit with warning!'
        syslog.syslog('Script exit with warning!')
        returnVal = 1
    except Exception:
        returnVal = -1
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
        print syslog.LOG_ERR, traceback.format_exc()
    finally:
        pass      

    return returnVal

try:

    import syslog
    import traceback
    import sys
    import subprocess
    import os
    import time

    syslog.syslog('400AP ppp script started, Internet connection not active')

    ## TWH, 11/14/2012:     Added code to parse command line args

    # Parse application name and command arguments
    appName = str(sys.argv[0])    
    pos1 = appName.rfind('/')
    appName = appName[pos1+1:len(appName)]

    appArgv = ''
    try: appArgv = str(sys.argv[1]).lower().rstrip()
    except: pass   

    if (appArgv == '') or ((appArgv != 'start') and (appArgv != 'stop')):
        print ''
        print 'Usage: ' + appName + ' [start|stop]'
        print ''
        print 'Configure ppp0 interface'
        print ''
        print '[start]    Bring up ppp0 network interface'
        print '[stop]  Tear down ppp0 network interface'
        print ''
        raise UserWarning 

    ## TWH, 11/13/2012:    pid check to see if more then just the current instance of the script is running

    # Is another instance of this script running?
    try:
        if len(get_pids(appName))>1:
            #print appName + ' is already running, exiting script'
            os._exit(0)
            
    except:
        #print syslog.LOG_ERR, traceback.format_exc()
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
        raise UserWarning

    ## TWH, 11/21/2012:    Must tear down ppp0 before import ATC_400AP opens serial port since both app share serial tty device

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
        res = main(appArgv)
        os._exit(int(res))
        
except UserWarning:
    #print 'Script exit with warning!'
    syslog.syslog('Script exit with warning!')
    os._exit(1)
    
except:
    #print syslog.LOG_ERR, traceback.format_exc()
    syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    os._exit(-1)