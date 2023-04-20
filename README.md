# ac_patcher
AnyConnect Patcher for Freedom

## Backstory
I got tired of AnyConnect always stealing/locking my route tables, especially after I started to use more containerization. It just got really frustrating to need to continually disconnect/reconnect, and/or hit up the systems admin person (me) to change the VPN side of things.

## How it works
The AnyConnect Linux Binary uses the following C++ method: ``CHostConfigMgr::StartInterfaceAndRouteMonitoring()``
The following Python script finds that method, then backtracks to where that method is being called from, and then NOPs out that call.
Since this address will change in each version of AnyConnect, I needed something that would do this process automatically, hence the scripting of `radare2`.

## Requirements

- AnyConnect must installed

## How to use it.

### Use at workstation

Install dependancies:
*Note: `radare2` is no longer included with Ubuntu after 20.04. You can download binaries from: https://github.com/radareorg/radare2/releases*

```
dpkg -i radare2_5.3.1_amd64.deb
```

*Note: As of 20210722 - `r2pipe` is not compatible with radare2 5.4.0 - the instructions on this page were tested with various versions up to 5.3.1*

```
pip3 install r2pipe
```

#### Run the patcher.
This will stop the system service, dissassemble the binary looking for the methods, and patch it out and then restart the service.
You'll need to ``sudo`` this for elevated privileges, due to the following:
1. the default installation directory ``/opt/cisco/anyconnect/`` requires elevated privileges for writing
1. stopping/starting the `vpnagentd` service requires service management privs.

```
sudo ./anyconnect_patcher.py
```

### Use in container

*On host must be installed Docker with support docker-compose*

```
docker compose version
Docker Compose version v2.17.2
```

- All dependencies will be install inside container
- `ac_patcher` will be perform inside container which 
will be have permissions stop/start `vpnagentd` to host

#### Install and Run

```
docker compose build
docker compose up
...
Here will be logs of ac_patcher
...
docker compose down
```

or

```
docker compose up --build
...
Here will be logs of ac_patcher
...
docker compose down
```

## Version Compatibility:
Tested / Confirmed with:
- 4.8.03036
- 4.9.00086
- 4.9.01095
- 4.9.02028 (Unable to test, Mac only)_
- 4.9.0304x
- 4.9.04053
- 4.9.05042
- 4.9.06037
- 4.10.00093
- 4.10.01075
- 4.10.04071
