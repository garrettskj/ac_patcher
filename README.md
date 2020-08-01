# ac_patcher
AnyConnect Patcher for Freedom

## Backstory
I got tired of AnyConnect always stealing/locking my route tables, especially after I started to use more constainerization. It just got really frustrating to need to continually disconnect/reconnect, and/or hit up the systems admin person (me) to change the VPN side of things.

## How it works
The AnyConnect Binary uses the following C++ method: ``CHostConfigMgr::StartInterfaceAndRouteMonitoring()``
The following python script finds that method, then backtracks to where that method is being called from, and then NOPs out that call.
Since each version of AnyConnect this memory address will change, I needed something that would do this process automatically, hence the scripting of radare2.

## How to use it.
Install AnyConnect

*tested with 4.9.0086*

Install dependancies:

```
apt install radare2
pip3 install r2pipe
```

## Run the patcher.
This will stop the system service, dissassemble the binary looking for the methods, and patch it out and then restart the service.
You'll need to ``sudo`` this for elevated privileges, due to the following:
1. the default installation directory ``/opt/cisco/anyconnect/`` requires elevated privileges for writing
1. stopping/starting the vpnagentd service requires service management privs.

```
sudo ./anyconnect_patcher.sh
```

