#!/usr/bin/python

##------------------------------------------------------------------------------------------------------------------
## Module: ppp-keepalive.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 11/15/2012)    :    Initial release
##    V1.0.1    (Thomas W. Heck, 11/21/2012)    :    Code cleanup
##    V2.1.0    (Thomas W. Heck, 01/29/2013)    :    Demo Release V2.1
##------------------------------------------------------------------------------------------------------------------

##------------------------------------------------------------------------------------------------------------------
## Description:
## 
## This script is used in conjunction with demoPPP.py to maintain a PPP connection.
## The script will determine if there is an active Internet connection.  If no connection
## is found the script will execute 'demoPPP.py start'.  You can run this in a cron job
## to eliminate the chance that connectivity to the 400AP is lost either by fault of the 
## pppd package, cellular network or the module has become unresponsive.  This is a
## consideration you must consider when deploying remote cellular applications in the  
## field.  It is recommended that this is handled by your application code.  This script 
## is only offered as an example of how to handle this condition.
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

import urllib2
import traceback
import time
import subprocess
import syslog
import os
import sys

def internet_on(URL='www.google.com',timeOut=10):
    try:
        response=urllib2.urlopen(URL,timeout=timeOut)
        return True
    except urllib2.URLError: pass
    return False

def get_pids(process_name):
    ## TWH, 11/13/2012:  Recoded to return a list of pids, return list without whitespace characters
    return subprocess.check_output('pidof ' + str(process_name),shell=True).rstrip().split(' ')  

def main():

    try:

        # Parse application name and command arguments
        appName = str(sys.argv[0])    
        pos1 = appName.rfind('/')
        appName = appName[pos1+1:len(appName)]

        #print appName

        # Is another instance of this script running?
        try:
            pids = get_pids(appName)
            #print str(pids)
            if len(pids)>1:
                #print appName + ' is already running, exiting script'
                return 0
        except:
            #print syslog.LOG_ERR, traceback.format_exc()
            syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
            return -1

        testURL = 'http://www.google.com'
        if internet_on(testURL,10) == True:
            #print '400AP ppp script exited, Internet connection is active'
            return 0

        #Bring up ppp0 network interface
        subprocess.call('/opt/demo400ap/scripts/demoPPP.py start',shell=True)
            
    except:
        #print syslog.LOG_ERR, traceback.format_exc()
        syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
        return -1

    return 0

try:
    if __name__ == "__main__":
        res = main()
        os._exit(int(res))
except:
    #print syslog.LOG_ERR, traceback.format_exc()
    syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    os._exit(-1)
