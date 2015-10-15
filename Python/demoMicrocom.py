#!/usr/bin/python

##------------------------------------------------------------------------------------------------------------------
## Module: demoMicrocom.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 12/02/2011)    :    Initial release
##    V1.0.1    (Thomas W. Heck, 06/29/2012)    :    Added code to remove ppp0 network interface
##    V1.2.0    (Thomas W. Heck, 01/11/2013)    :    Changed ppp removal bash script to ppp_cleanup() method
##                                                   Re-worded the microcom message for clarification
##                                                   Cleaned up error handling
##                                                   Added configuration file loading to determine if 400AP has
##                                                   production hardware
##    V1.2.1    (Thomas W. Heck, 01/17/2013)    :    Added delay before powering on Plug-in Terminus, allows 
##                                                   PWRMON to drop after UART set to high-Z and VBUS disabled
##    V2.1.0    (Thomas W. Heck, 01/29/2013)    :    Demo Release V2.1
##------------------------------------------------------------------------------------------------------------------

##------------------------------------------------------------------------------------------------------------------
## NOTES
##  1.)  Module works with all 400AP models
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

        rtnList = myGPIO.initIO ()
        if rtnList[0] == -1: raise UserWarning

        #High-Z all UART pins driving into Plug-in Terminus
        rtnList = myGPIO.setUartEnable(1)
        if rtnList[0] == -1: raise UserWarning

        #Inhibit VBUS voltage
        rtnList = myGPIO.setEnableVbus(0)
        if rtnList[0] == -1: raise UserWarning

        #Give the USB host some time to disconnect radio
        time.sleep(4)

        rtnList = myGPIO.setPoweredState(1,15)  
        if rtnList[0] == -1 or rtnList[0] == -2: raise UserWarning

        #Enable UART I/O
        rtnList = myGPIO.setUartEnable(0)
        if rtnList[0] == -1: raise UserWarning

        time.sleep(2)

        #Clear Screen
        cmdLine = "clear"
        res = subprocess.call(cmdLine, shell=True)

        print '################################################'
        print 'MICROCOM TERMINAL (AT Command port on ttyS1):'
        print '################################################'
        print ''
        print 'Type AT commands (Example:  at+cgmm <ENTER>)'
        print ''
        print 'or'
        print ''
        print 'Select CTRL-X to exit script'
        print ''
        print '################################################'
        print ''

        cmdLine = "microcom -s 115200 /dev/ttyS1"
        res = subprocess.call(cmdLine, shell=True)

        #High-Z all UART pins driving into Plug-in Terminus
        rtnList = myGPIO.setUartEnable(1)
        if rtnList[0] == -1: raise UserWarning
       
        #Inhibit VBUS voltage
        rtnList = myGPIO.setEnableVbus(0)
        if rtnList[0] == -1: raise UserWarning

        #Turn off Plug-in Terminus
        rtnList = myGPIO.setPoweredState(0,15)
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

    return (returnVal)

try:
    
    import syslog
    import traceback
    import sys
    import traceback
    import subprocess
    import os
    import time

    #Clear Screen
    cmdLine = "clear"
    res = subprocess.call(cmdLine, shell=True)

    #Kill running pppd processes   
    res = ppp_cleanup()
    if res == -1: raise UserWarning   

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

