#!/usr/bin/python

##------------------------------------------------------------------------------------------------------------------
## Module: demoMenu.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 12/02/2011)    :    Initial release
##    V1.0.1    (Thomas W. Heck, 01/26/2012)    :    Added GPS demo
##    V1.0.2    (Thomas W. Heck, 06/29/2012)    :    Added PPP & Router demo
##    V1.1.0    (Thomas W. Heck, 01/11/2013)    :    Removed menu reload.  Menu exits after selected demo script exits
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

import traceback
import os, inspect 
import subprocess
import time

class properties:
    APP_PATH = ""

def main():

    #Get current application path
    try:

        rtn = -1
        
        if '__file__' not in locals():
            __file__ = inspect.getframeinfo(inspect.currentframe())[0]
        properties.APP_PATH = os.path.dirname(os.path.abspath(__file__))

        cmdLine = "python " + properties.APP_PATH + "/menu.py"
        res = subprocess.call(cmdLine, shell=True)

        if res == 1:
            cmdLine = 'nano ' + properties.APP_PATH + '/../demo400ap.conf'
            print 'Executing Script:   ' + cmdLine
            time.sleep(2)
            res = subprocess.call(cmdLine, shell=True)

        elif res == 2:

            cmdLine = properties.APP_PATH + "/demoMicrocom.py"
            print 'Executing Script:   ' + cmdLine
            time.sleep(2)
            res = subprocess.call(cmdLine, shell=True)

        elif res == 3:
            cmdLine = properties.APP_PATH + "/demoGps.py"
            print 'Executing Script:   ' + cmdLine
            time.sleep(2)
            res = subprocess.call(cmdLine, shell=True)

        elif res == 4:
            cmdLine = properties.APP_PATH + "/demoPPP.py start"
            print 'Executing Script:   ' + cmdLine
            time.sleep(2)
            res = subprocess.call(cmdLine, shell=True)
            
        elif res == 5:
            cmdLine = properties.APP_PATH + "/demoPPP.py stop"
            print 'Executing Script:   ' + cmdLine
            time.sleep(2)
            res = subprocess.call(cmdLine, shell=True)

        elif res == 6:
            cmdLine = properties.APP_PATH + "/demoRouter.py start"
            print 'Executing Script:   ' + cmdLine
            time.sleep(2)
            res = subprocess.call(cmdLine, shell=True)
            
        elif res == 7:
            cmdLine = properties.APP_PATH + "/demoRouter.py stop"
            print 'Executing Script:   ' + cmdLine
            time.sleep(2)
            res = subprocess.call(cmdLine, shell=True)
            
        elif res == 8:
            pass
            
        rtn = 0

    except KeyboardInterrupt:
        pass
    except Exception: print traceback.format_exc()

    return(rtn)

if __name__ == "__main__":
    main()
