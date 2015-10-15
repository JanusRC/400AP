##------------------------------------------------------------------------------------------------------------------
## Module: menu.py
## Release Information:
##    V1.0.0    (Thomas W. Heck, 12/02/2011)    :    Initial release
##    V1.0.1    (Thomas W. Heck, 06/29/2012)    :    Added GPS, PPP and Router demo
##    V1.0.2    (Thomas W. Heck, 0`/17/2013)    :    Corrected typo in menu
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

import curses
import sys

class properties:
    APP_VER = "v2.1"

def main():

    #Function displays main menu and returns user selection    

    #Return:
    #    -1:    Exception occurred in Function
    #     0:    Exit character entered
    # 1 - 4:    Menu selection 
    
    EXIT_CHR ="x"
    MENU_START = 1
    MENU_END = 7

    try:
        
        screen.timeout(10000)
        
        while True:
            
            screen.clear()
            screen.addstr("400AP Demonstration (" + properties.APP_VER + ")\n\n")
            screen.addstr("1)\tEdit demo configuration file (nano)\n")
            screen.addstr("2)\tOpen terminal to send AT commands (microcom)\n")
            screen.addstr("3)\tStart GPS demo (demoGps.py)\n")
            screen.addstr("4)\tStart a PPP connection (demoPPP.py start)\n")
            screen.addstr("5)\tStop a PPP connection (demoPPP.py stop)\n")
            screen.addstr("6)\tStart router (demoRouter.py start)\n")
            screen.addstr("7)\tStop router (demoRouter.py stop)\n")
            screen.addstr("x)\tExit\n\n")
            screen.addstr("\rSelection: ")
        
            try:
                event = str(screen.getkey())
            except:
                event = ''

            #event = str(chr(screen.getch()))
            if event.isalnum() == 1:
                screen.addstr("\rSelection: " + event)
                if event.isalpha() == 1:
                    if event == EXIT_CHR:
                        return (0)
                elif event.isdigit() == 1:
                    BYTE = int(event)
                    if ((BYTE >= MENU_START) and (BYTE <= MENU_END)):
                        #return menu selection
                        return (BYTE)
            else: screen.addstr("\rSelection: ?")
                
    
    except Exception:
        return (-1)

#initialize screen
try:
    screen = curses.initscr()
    curses.noecho()
except Exception: exit(-2)

try:
    curses.curs_set(0)
except Exception: pass

try:
    screen.keypad(0)
except Exception: exit(-2)

res = main()

try:
    screen.clear()
    curses.endwin()
except Exception: exit(-2)

exit (res)