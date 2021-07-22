#!/usr/bin/env python3

import os
import r2pipe

AC_PATH = '/opt/cisco/anyconnect/bin/'

def get_the_evil_method():
 r = r2pipe.open(AC_PATH + 'vpnagentd')
 print ("Opening and analyzing, 15 seconds...")
 r.cmd('aaa')
 method_location = r.cmd("afl | grep StartInterface | awk \'{print $1}\'").rstrip()
 r.quit()
 return method_location

def find_the_call(method_location):
 r = r2pipe.open(AC_PATH + 'vpnagentd')
 r.cmd('aaa')
 print ("Opening and finding the method now, 15 seconds...")
 r.cmd('s ' + method_location )
 called_from = r.cmd("axt | awk \'{print $2}\'").rstrip()
 r.quit()

 return called_from

def nop_the_call(called_from):
  if called_from != '':
    r = r2pipe.open(AC_PATH + 'vpnagentd', flags=['-w'])
    r.cmd('aaa')
    r.cmd('s ' + called_from )
    r.cmd('wx 9090909090')
    r.quit()
    return True
  else:
    return False

## Stop the Anyconnect Service.
os.system("systemctl stop vpnagentd")

## Get the Method offset in the vpnagentd binary
method_location = get_the_evil_method()
print ("Found method @ " + method_location)

## Locate where that method is being called from
called_from = find_the_call(method_location)
print ("Looks like it's called from: " + called_from)

## NOP out that call.
status = nop_the_call(called_from)
if status == True:
    print ("Patching Completed Successfully")
else:
    print ("Patching Failed, maybe already done?")

## Restart the Anyconnect Service.
os.system("systemctl restart vpnagentd")
