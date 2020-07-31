#!/bin/bash

USERNAME=vpnuser
TWOFA=true
PIN=1234
VPN_ENDPOINT="vpn.someplace.com"

if [ "$TWOFA" = true ] ; then
  LOGINSTR="0\n$USERNAME\n$PIN$1\n"
else
  LOGINSTR="0\n$USERNAME\n$1\n"
fi

# put the answers in a tmp file (TODO: fix this)
echo -e $LOGINSTR > /tmp/answers.txt

# find the path to the anyconnect executables
ciscopath="$(dirname $(find /opt/cisco -depth -name vpnagentd))"

# make sure the anyconnect daemon is running
[ $(pidof vpnagentd) ] || $ciscopath/vpnagentd

# connect
echo $ciscopath
$ciscopath/vpn -s < /tmp/answers.txt connect $VPN_ENDPOINT
