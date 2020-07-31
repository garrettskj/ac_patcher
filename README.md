# ac_patcher
AnyConnect Patcher for Freedom

## Backstory
I got tired of AnyConnect always stealing/locking my route tables, especially after I started to use more constainerization. It just got really frustrating to need to continually disconnect/reconnect, and/or hit up the systems admin person (me) to change the VPN side of things.

## How it works
I dissassembled the AnyConnect Binary and figured out the methods it was using to monitor the route tables. I simply removed those calls.

## How to use it.
Install AnyConnect
*tested with 4.x*

Install dependancies:

```
apt install radare2
pip3 install r2pipe
```

## Run the patcher.
This will stop the system service, dissassemble the binary looking for the methods, and patch it out and then restart the service.

```
sudo ./anyconnect_patcher.sh
```

