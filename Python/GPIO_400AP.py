##------------------------------------------------------------------------------------------------------------------
## Module: GPIO_400AP.py
## Release Information:
##    V2.0.0    (Thomas W. Heck, 06/29/2012)    :    Initial release
##    V2.0.1    (Thomas W. Heck, 11/13/2012)    :    Altered isPowered method to fix PWRMON detection
##    V2.0.2    (Thomas W. Heck, 01/11/2013)    :    Changed module to a class
##                                                   Push in PRODUCTION and CGMM for configuration options
##                                                   Added power state change verification to
##                                                   setPoweredState(state, timeOut), Changed initIO to check
##                                                   whether IO was already configured, skip if configured
##                                                   Added confGPIO and getGPIO methods
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
import time
import syslog

class gpio:

    def __init__(self, PRODUCTION, CGMM):

        self.GRN_LED = '81'
        
        self.EXT_GPIO_1 = '37'   #External 20-pin Header Pin 2
        self.EXT_GPIO_2 = '83'   #External 20-pin Header Pin 4
        self.EXT_GPIO_3 = '96'   #External 20-pin Header Pin 1
        self.EXT_GPIO_4 = '97'   #External 20-pin Header Pin 3

        self.MODE_BUTTON = '82'
        self.UART_ENABLE = '94'
        self.PWRMON = '95'
        self.ON_OFF = '104'
        self.RESET = '105'
        self.GPS_RESET = '106'
        self.SERVICE = '108'
        self.ENABLE_SUPPLY = '111'

        self.OUTPUT = 1
        self.INPUT = 0
        
        if PRODUCTION == True:

            self.RED_LED = '76'
            #print 'RED_LED = ' + str(self.RED_LED)
            
            self.ENABLE_VBUS = '99'
            #print 'ENABLE_VBUS = ' + str(self.ENABLE_VBUS)
            
        else:

            self.ENABLE_VBUS = '113'
            #print 'ENABLE_VBUS = ' + str(self.ENABLE_VBUS)

        if CGMM == 'HE910':
            self.ON_HOLD_TIME = 5.2
            self.OFF_HOLD_TIME = 3.2
            self.BOOT_DELAY_TIME = 1.2
        elif CGMM == 'CC864-DUAL':
            self.ON_HOLD_TIME = 1.2
            self.OFF_HOLD_TIME = 2.2
            self.BOOT_DELAY_TIME = 1.2
        else:
            self.ON_HOLD_TIME = 1.2
            self.OFF_HOLD_TIME = 2.2
            self.BOOT_DELAY_TIME = 1.2

        #print 'ON_HOLD_TIME = ' + str(self.ON_HOLD_TIME)
        #print 'OFF_HOLD_TIME = ' + str(self.OFF_HOLD_TIME)
        #print 'BOOT_DELAY_TIME = ' + str(self.BOOT_DELAY_TIME)    

        self.PRODUCTION = PRODUCTION
        
        #print 'PRODUCTION = ' + str(self.PRODUCTION)
        
        self.CGMM = CGMM
        
        #print 'CGMM = ' + str(self.CGMM)

    def setpins(self, pin_no, pin_direction):
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
        
        try:
            gpioopnum = "gpio%s" % (str(pin_no), )
            pin1dir = open("/sys/class/gpio/"+gpioopnum+"/direction","w")
            if pin_direction == 1:
                pin1dir.write("high")
            else:
                pin1dir.write("in")
                pin1dir.close()
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)

    def writepins(self, pin_no, pin_state):
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            gpioopnum = "gpio%s" % (str(pin_no), )
            pin1val = open("/sys/class/gpio/"+gpioopnum+"/value","w")
            pin1val.write(str(pin_state))
            pin1val.close()
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)

    def readpins(self, pin_no):
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            gpioopnum = "gpio%s" % (str(pin_no), )
            pin1val = open("/sys/class/gpio/"+gpioopnum+"/value","r")
            state = int(pin1val.read())
            #print 'GPIO' + str(pin_no) + ' state: ' + str(state)
            rtnList[1] = state
            pin1val.close()
            rtnList[0] = 1
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def unexport_pins(self, pins):
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            fp4 = open("/sys/class/gpio/unexport","w")
            fp4.write(str(pins))
            fp4.close()
            rtnList[0] = 0
        except IOError: rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def export_pin(self, pins):
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    GPIO already created
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            #print 'export GPIO' + str(pins) + " creating resource"
            fp1 = open("/sys/class/gpio/export","w")
            fp1.write(str(pins))
            #print 'export GPIO' + str(pins) + " closing resource"
            fp1.close()
            rtnList[0] = 0
        except IOError: rtnList[0] = -2
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setGrnLed (self, state):
        # sets Green LED state
        # state:
        #    0:    LED not illuminated
        #    1:    LED illuminated
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
     
        try:
            res = self.export_pin(self.GRN_LED)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.GRN_LED, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.GRN_LED, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setRedLed (self, state):
        # sets Red LED state
        # state:
        #    0:    LED not illuminated
        #    1:    LED illuminated
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
     
        if self.PRODUCTION == False:
            rtnList[0] = 0
            return (rtnList)
     
        try:
            res = self.export_pin(self.RED_LED)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.RED_LED, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.RED_LED, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setEnableSupply (self, state):
        # sets Enable Supply state
        # state:
        #    0:    Plug-in Terminus power supply is enabled
        #    1:    Plug-in Terminus power supply is disabled
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            res = self.export_pin(self.ENABLE_SUPPLY)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.ENABLE_SUPPLY, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.ENABLE_SUPPLY, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setOnOff (self, state):
        # sets ON_OFF state
        # state:
        #    0:    Plug-in Terminus run state
        #    1:    Plug-in Terminus toggle state
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            res = self.export_pin(self.ON_OFF)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.ON_OFF, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.ON_OFF, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setReset (self, state):
        # sets RESET state
        # state:
        #    0:    Plug-in Terminus run state
        #    1:    Plug-in Terminus reset state
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            res = self.export_pin(self.RESET)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.RESET, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.RESET, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setService (self, state):
        # sets SERVICE state
        # state:
        #    0:    GSM400AP Service mode disabled
        #    1:    GSM400AP Service mode enable
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            res = self.export_pin(self.SERVICE)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.SERVICE, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.SERVICE, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setGpsReset (self, state):
        # sets GPS Reset state
        # state:
        #    0:    GSM400AP V1.1 MS20 GPS receiver reset run state
        #    1:    GSM400AP V1.1 MS20 GPS receiver reset reset state
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            res = self.export_pin(self.GPS_RESET)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.GPS_RESET, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.GPS_RESET, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setEnableVbus (self, state):
        # sets GPS ENABLE_VBUS voltage
        # state:
        #    0:    VBUS = 0Vdc
        #    1:    VBUS = 5Vdc
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            res = self.export_pin(self.ENABLE_VBUS)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.ENABLE_VBUS, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.ENABLE_VBUS, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setUartEnable (self, state):
        # sets UART Enable state
        # state:
        #    0:    UART I/O drive logic
        #    1:    UART I/O High-Z
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
            res = self.export_pin(self.UART_ENABLE)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.UART_ENABLE, self.OUTPUT)
            if res[0] == -1: return (rtnList)
            res = self.writepins(self.UART_ENABLE, state)
            if res[0] == -1: return (rtnList)
            rtnList[0] = 0
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def getModeButton (self):
        # reads Mode Button state
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
        # return data:
        #    0:    Button activated
        #    1:    Button de-activated
    
        try:
            res = self.export_pin(self.MODE_BUTTON)
            if res[0] == -1: return (rtnList)
            res = self.setpins(self.MODE_BUTTON, self.INPUT)
            if res[0] == -1: return (rtnList)
            res = self.readpins(self.MODE_BUTTON)
            if res[0] == -1: return (rtnList)
            rtnList[1] = res[1]
            rtnList[0] = 1
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)

    def confGPIO (self, GPIO, DIR=0, STATE=0):
        # Configure GPIO as INPUT or OUTPUT

        rtnList = [-1,-1]    #[return status,return data]
        
        # GPIO:
        #    1:    EXT_GPIO1
        #    2:    EXT_GPIO2
        #    3:    EXT_GPIO3
        #    4:    EXT_GPIO4
        # DIR:
        #    0:    INPUT        Default
        #    1:    OUTPUT
        # STATE: (Initial Condition when setting as Output)
        #    0:    Logic '0'    Default
        #    1:    Logic '1'
        
        # return status:
        #   -2:    Input parameter out of range
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
        # return data:
        #    0:    GPIO Logic '0'
        #    1:    GPIO Logic '1'

        try:

            #Check for valid GPIO 
            if GPIO==1:
                GPIO = self.EXT_GPIO_1
            elif GPIO==2:
                GPIO = self.EXT_GPIO_2
            elif GPIO==3:
                GPIO = self.EXT_GPIO_3
            elif GPIO==4:
                GPIO = self.EXT_GPIO_4
            else:
                rtnList[0]==-2
                return(rtnList)

            #Check for valid DIR
            if DIR==0:
                DIR=self.INPUT
            elif DIR==1:
                DIR=self.OUTPUT
            else:
                rtnList[0]==-2
                return(rtnList)
            
            #Check for valid State
            if STATE==0:
                pass
            elif STATE==1:
                pass
            else:
                rtnList[0]==-2
                return(rtnList)

            #Configure GPIO if needed
            res = self.export_pin(GPIO)
            if res[0] == -1: return (rtnList)
            
            #Configure GPIO direction
            if DIR==self.INPUT:
                res = self.setpins(GPIO, DIR)
                if res[0] == -1: return (rtnList)
            else:
                res = self.setpins(GPIO, DIR)
                if res[0] == -1: return (rtnList)
                res = self.writepins(GPIO, STATE)
                if res[0] == -1: return (rtnList)

            rtnList[0] = 0
            
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    
    def getGPIO (self, GPIO):
        # read selected GPIO state

        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -2:    Invalid GPIO
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
        # return data:
        #    0:    GPIO Logic '0'
        #    1:    GPIO Logic '1'

        try:

            if GPIO==1:
                GPIO = self.EXT_GPIO_1
            elif GPIO==2:
                GPIO = self.EXT_GPIO_2
            elif GPIO==3:
                GPIO = self.EXT_GPIO_3
            elif GPIO==4:
                GPIO = self.EXT_GPIO_4
            else:
                rtnList[0]==-2
                return(rtnList)

            #Test to determine if GPIO has already been created
            res = self.export_pin(GPIO)
            if res[0] == -1: return (rtnList)
            elif res[0] == 0:
                #If GPIO was exported by within this method then set as input
                res = self.setpins(GPIO, self.INPUT)
                if res[0] == -1: return (rtnList)
            
            res = self.readpins(GPIO)
            if res[0] == -1: return (rtnList)
            rtnList[1] = res[1]
            rtnList[0] = 1

        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    
    def isPowered (self):
        # reads PWRMON pin
    
        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
        # return data:
        #    0:    Plug-in Terminus is powered on
        #    1:    Plug-in Terminus is powered off
    
        try:
            
            res = self.export_pin(self.PWRMON)
            if res[0] == -1: return (rtnList)      
            
            res = self.setpins(self.PWRMON, self.INPUT)
            if res[0] == -1: return (rtnList)
            
            res = self.readpins(self.PWRMON)
            if res[0] == -1: return (rtnList)
            
            rtnList[1] = res[1]
            
            rtnList[0] = 1
            
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def initIO (self):
        # Set all I/O to default states
        # Method will only create GPIO if they are not already created


        rtnList = [-1,-1]    #[return status,return data]
        # return status:
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:

            #Test to determine if GPIO has already been created
            res = self.export_pin(self.RESET)
            if res[0] == -1: return (rtnList)
            elif res[0] == 0:
                #RESET set to run state
                res = self.setReset(0)
                if res[0] == -1: return (rtnList)

            #Test to determine if GPIO has already been created
            res = self.export_pin(self.ON_OFF)
            if res[0] == -1: return (rtnList)
            elif res[0] == 0:       
                #ON_OFF set to run state
                res = self.setOnOff(0)
                if res[0] == -1: return (rtnList)

            #Test to determine if GPIO has already been created
            res = self.export_pin(self.SERVICE)
            if res[0] == -1: return (rtnList)
            elif res[0] == 0:       
                #SERVICE set to run state
                res = self.setService(0)
                if res[0] == -1: return (rtnList)

            #Test to determine if GPIO has already been created
            res = self.export_pin(self.GPS_RESET)
            if res[0] == -1: return (rtnList)
            elif res[0] == 0:       
                res = self.setGpsReset(0)
                if res[0] == -1: return (rtnList)

            #Test to determine if GPIO has already been created
            res = self.export_pin(self.ENABLE_VBUS)
            if res[0] == -1: return (rtnList)
            elif res[0] == 0:       
                #Inhibit VBUS voltage
                res = self.setEnableVbus(0)
                if res[0] == -1: return (rtnList)

            #Test to determine if GPIO has already been created
            res = self.export_pin(self.UART_ENABLE)
            if res[0] == -1: return (rtnList)
            elif res[0] == 0:       
                #High-Z all UART pins driving into Plug-in Terminus
                res = self.setUartEnable(1)
                if res[0] == -1: return (rtnList)

            #Test to determine if GPIO has already been created
            res = self.export_pin(self.ENABLE_SUPPLY) 
            if res[0] == -1: return (rtnList)
            elif res[0] == 0:
                #Enable Plug-in Terminus power supply
                res = self.setEnableSupply(0)
                if res[0] == -1: return (rtnList)
                #Delay to allow supply to stabilize, before application
                #attempts to access radio
                time.sleep(2)

            rtnList[0] = 0

        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)
    
    def setPoweredState(self, state, timeOut):
        # Turn Plug-in Terminus on or off
        # state:
        #    0:    Turn Plug-in Terminus Off
        #    1:    Turn Plug-in Terminus On
    
        rtnList = [-1,-1]    #[return status,return data]                #Require delay after releasing ONOFF
        # return status:
        #   -2:    Timeout occurred
        #   -1:    Exception occurred
        #    0:    No errors occurred, no return data
        #    1:    No errors occurred, return data
    
        try:
    
            # Check if Plug-in Terminus is powered
            rtnList = self.isPowered()
            if rtnList[0] == -1: return (rtnList)
            
            if rtnList[1] == 1:
                print 'Plug-in Terminus is off'
                if state == 0:                #Require delay after releasing ONOFF
                    rtnList[0] = 0
                    return(rtnList)
            else:
                print 'Plug-in Terminus is on'
                if state == 1:
                    rtnList[0] = 0
                    return(rtnList)
 
            if state == 1:
    
                print 'Powering On' + "\r\n"
    
                # Toggle ON_OFF pin
                res = self.setOnOff(1)
                if res[0] == -1: return (rtnList)

                time.sleep(self.ON_HOLD_TIME)
    
                res = self.setOnOff(0)
                if res[0] == -1: return (rtnList)
    
                #Wait for module to turn on
                start = time.time()
                rtnList[1] = 1
                while (rtnList[1] != 0):                #Require delay after releasing ONOFF
                    rtnList = self.isPowered()
                    print 'Waiting for power state to change'
    
                    if (time.time() - start > timeOut):
                        print 'Plug-in Terminus failed to turn on'
                        syslog.syslog('Plug-in Terminus failed to turn on')
                        rtnList[0] = -2
                        return (rtnList)
    
                    time.sleep(1)

            else:
        
                print 'powering off' + "\r\n"
    
                # Toggle ON_OFF pin
                res = self.setOnOff(1)
                if res[0] == -1: return (rtnList)
    
                time.sleep(self.OFF_HOLD_TIME)
    
                res = self.setOnOff(0)
                if res[0] == -1: return (rtnList)
    
                #Wait for module to turn on
                start = time.time()
                rtnList[1] = 0
                while (rtnList[1] != 1):
    
                    rtnList = self.isPowered()
                    print 'Waiting for power state to change'
    
                    if (time.time() - start > timeOut):
                        print 'Plug-in Terminus failed to turn off'
                        syslog.syslog('Plug-in Terminus failed to turn off')
                        rtnList[0] = -2
                        return (rtnList)
    
                    time.sleep(1)
    
            rtnList = self.isPowered()
            if rtnList[0] == -1: return (rtnList)
            if rtnList[1] == 1:
                print 'Plug-in Terminus is off'
            else:
                print 'Plug-in Terminus is on'
                #Require delay after releasing ONOFF
                time.sleep(self.BOOT_DELAY_TIME)
    
            rtnList[0] = 0
    
        except Exception: syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
    
        return (rtnList)