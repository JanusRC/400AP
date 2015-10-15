#!/usr/bin/python

##------------------------------------------------------------------------------------------------------------------
## Module: demoRouter.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 06/29/2012)    :    Initial release
##    V1.2.0    (Thomas W. Heck, 11/15/2012)    :    Added Start | Stop command line options
##                                                   Uses demoPPP.py script to manage ppp0
##    V1.3.0    (Thomas W. Heck, 12/05/2012)    :    Code cleanup, added exception handling
##                                                   to kill_process() method
##    V1.4.0    (Thomas W. Heck, 01/11/2013)    :    main method now exits with status code 1 
##                                                   when errors occur.
##    V2.1.0    (Thomas W. Heck, 01/29/2013)    :    Demo Release V2.1
##------------------------------------------------------------------------------------------------------------------

##------------------------------------------------------------------------------------------------------------------
## Description:
## 
## This script configures the 400AP as a cellular router. This is one way to configure 
## the 400AP as a NAT router and was created as an example.  It is recommend to execute
## this at start-up via an S script in the /etc/init.d directory.
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

def kill_process(process_name):

    try:

        try:
            #kill all running pppd processes
            while(1):
                pids = get_pids(process_name)         
                os.kill(int(pids[0]),9)
                #print 'Process killed {' + str(pid[0]) + '}'
        except subprocess.CalledProcessError, e:
            #print 'No PPP process running: ' + str(e)
            pass
        except:
            #print syslog.LOG_ERR, traceback.format_exc()
            syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
            return -1    

    except:
        #print syslog.LOG_ERR, traceback.format_exc()
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
        return -1

    return 0

## main code
def main(appArgv=''):

    returnVal = -1
    # return status:
    #   -1:    Un-handled Exception occurred
    #    0:    No errors occurred, no return data
    #    1:    Error[s] occurred

    try:

        if appArgv == 'start':

            #Bring up ppp0 network interface

            #Bring down eth0
            res = subprocess.call('ifconfig eth0 down', shell=True)
            
            time.sleep(5)
    
            #Bring up eth0
            res = subprocess.call('ifconfig eth0 192.168.2.1 netmask 255.255.255.0 up', shell=True)
            
            time.sleep(5)
    
            # Enable masquerading
            res = subprocess.call('iptables -t nat -A POSTROUTING -o ppp0 -j MASQUERADE', shell=True)
    
            # Enable routing
            res = subprocess.call('echo 1 > /proc/sys/net/ipv4/ip_forward', shell=True)
    
            # Start dnsmasq
            res = subprocess.call('dnsmasq', shell=True)

            # Bring up ppp0 network interface
            res = subprocess.call('/opt/demo400ap/scripts/demoPPP.py start', shell=True)
    
            returnVal = 0

        else:
            
            # Tear down ppp0 network interface
            res = subprocess.call('/opt/demo400ap/scripts/demoPPP.py stop', shell=True)
        
            # Kill dnsmasq process
            kill_process('dnsmasq')
            
            # Disable routing
            res = subprocess.call('echo 0 > /proc/sys/net/ipv4/ip_forward', shell=True)
            
            # Flush all rules
            res = subprocess.call('iptables -F', shell=True)
            
            #Bring down eth0
            res = subprocess.call('ifconfig eth0 down', shell=True)
            
            time.sleep(5)
    
            #Bring up eth0
            res = subprocess.call('ifconfig eth0 192.168.1.50 netmask 255.255.255.0 up', shell=True)
            
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

    syslog.syslog('400AP router configuration script started')

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
        print 'Configure 400AP as Cellular NAT router'
        print ''
        print '[start] Bring up router'
        print '[stop]  Tear down all router processes'
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
    