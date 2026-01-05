#!/usr/bin/env python3

import os
import r2pipe

# Updated path for Cisco Secure Client (v5.x+)
AC_PATH = '/opt/cisco/secureclient/bin/'

def get_the_evil_method(function_name):
    """
    Finds the address of a function by name using radare2 analysis.
    """
    try:
        r = r2pipe.open(AC_PATH + 'vpnagentd')
        print(f"Opening and analyzing to find {function_name}, please wait...")
        r.cmd('aaa')
        # specific grep to find the function address
        method_location = r.cmd(f"afl | grep {function_name} | awk '{{print $1}}'").rstrip()
        r.quit()
        return method_location
    except Exception as e:
        print(f"Error finding method {function_name}: {e}")
        return ""

def find_the_call(method_location):
    """
    Finds where the method is called from (Cross References).
    """
    try:
        r = r2pipe.open(AC_PATH + 'vpnagentd')
        r.cmd('aaa')
        print(f"Finding calls to {method_location}, please wait...")
        r.cmd(f's {method_location}')
        # axt = analyze xrefs to
        called_from = r.cmd("axt | awk \'{print $2}\'").rstrip().split('\n')
        r.quit()
        return called_from
    except Exception as e:
        print(f"Error finding calls: {e}")
        return []

def patch_call_return_zero(called_from):
    """
    Patches the instruction at 'called_from' to return 0 (Success) immediately.
    Replaces the 5-byte CALL with:
    4831c0: xor rax, rax (Return 0)
    9090:   nop nop      (Padding)
    """
    if called_from and called_from != '':
        try:
            r = r2pipe.open(AC_PATH + 'vpnagentd', flags=['-w'])
            r.cmd('aaa')
            r.cmd(f's {called_from}')
            r.cmd('wx 4831c09090')
            r.quit()
            return True
        except Exception as e:
            print(f"Error patching at {called_from}: {e}")
            return False
    else:
        return False

def main():
    if os.geteuid() != 0:
        print("Error: This script must be run as root (sudo).")
        exit(1)

    ## Stop the Anyconnect Service.
    print("Stopping vpnagentd service...")
    os.system("systemctl stop vpnagentd")

    # ---------------------------------------------------------
    # Patch 1: StartInterfaceAndRouteMonitoring
    # Prevents the agent from locking the route table.
    # ---------------------------------------------------------
    method_location = get_the_evil_method("StartInterface")
    if method_location:
        print(f"Found method StartInterface @ {method_location}")
        called_from = find_the_call(method_location)
        print(f"Calls found at: {called_from}")

        if not called_from or called_from == ['']:
            print("No callers found. Patch maybe already done?")
        else:
            for cf in called_from:
                if patch_call_return_zero(cf):
                    print(f"Successfully patched StartInterface call at {cf}")
                else:
                    print(f"Failed to patch StartInterface call at {cf}")
    else:
        print("Could not find method StartInterface.")

    print("-" * 30)

    # ---------------------------------------------------------
    # Patch 2: VerifyFileSignatureCollective::IsValid
    # Prevents the agent from verifying the binary integrity (Anti-Tamper).
    # ---------------------------------------------------------
    print("Now patching FileSignature verification")
    method_location = get_the_evil_method("VerifyFileSignatureCollective::IsValid")
    if method_location:
        print(f"Found method VerifyFileSignatureCollective::IsValid @ {method_location}")
        called_from = find_the_call(method_location)
        print(f"Calls found at: {called_from}")

        if not called_from or called_from == ['']:
            print("No callers found. Patch maybe already done?")
        else:
            for cf in called_from:
                if patch_call_return_zero(cf):
                    print(f"Successfully patched VerifyFileSignature call at {cf}")
                else:
                    print(f"Failed to patch VerifyFileSignature call at {cf}")
    else:
        print("Could not find method VerifyFileSignatureCollective::IsValid.")

    ## Restart the Anyconnect Service.
    print("Restarting vpnagentd service...")
    os.system("systemctl restart vpnagentd")
    print("Done.")

if __name__ == "__main__":
    main()
