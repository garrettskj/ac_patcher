#!/usr/bin/env python3
"""Patch AnyConnect/Secure Client's vpnagentd to stop it from taking over
route tables and to skip its own binary-signature verification.

Looks for an install under either the legacy AnyConnect path or the newer
Cisco Secure Client (v5.x+) path. See REPORTED_ISSUES.md for known-broken
versions and open questions.
"""

import os
import sys

import r2pipe

# Cisco renamed AnyConnect to Secure Client starting with v5.x and moved the
# install directory along with it. Support both so this still works on
# older 4.x installs.
CANDIDATE_AC_PATHS = (
    "/opt/cisco/secureclient/bin/",
    "/opt/cisco/anyconnect/bin/",
)


def find_ac_path():
    for path in CANDIDATE_AC_PATHS:
        if os.path.exists(path + "vpnagentd"):
            return path
    return None


def get_the_evil_method(ac_path, function_name):
    """Find the address of a function by name using radare2 analysis."""
    try:
        r = r2pipe.open(ac_path + "vpnagentd")
        print(f"Opening and analyzing to find {function_name}, please wait...")
        r.cmd("aaa")
        method_location = r.cmd(f"afl | grep {function_name} | awk '{{print $1}}'").rstrip()
        r.quit()
        return method_location
    except Exception as e:
        print(f"Error finding method {function_name}: {e}")
        return ""


def find_the_call(ac_path, method_location):
    """Find where a method is called from (cross references)."""
    try:
        r = r2pipe.open(ac_path + "vpnagentd")
        r.cmd("aaa")
        print(f"Opening and finding the method now, calls to {method_location}...")
        r.cmd(f"s {method_location}")
        called_from = r.cmd("axt | awk '{print $2}'").rstrip().split("\n")
        r.quit()
        return called_from
    except Exception as e:
        print(f"Error finding calls to {method_location}: {e}")
        return []


def nop_the_call(ac_path, called_from):
    """Replace the call with plain NOPs, leaving register state untouched."""
    if not called_from:
        return False
    try:
        r = r2pipe.open(ac_path + "vpnagentd", flags=["-w"])
        r.cmd("aaa")
        r.cmd(f"s {called_from}")
        r.cmd("wx 9090909090")
        r.quit()
        return True
    except Exception as e:
        print(f"Error patching at {called_from}: {e}")
        return False


def patch_call_return_zero(ac_path, called_from):
    """Replace the call with xor rax,rax; nop; nop, so the caller sees a
    successful (0) return value instead of whatever was left in rax."""
    if not called_from:
        return False
    try:
        r = r2pipe.open(ac_path + "vpnagentd", flags=["-w"])
        r.cmd("aaa")
        r.cmd(f"s {called_from}")
        r.cmd("wx 4831c09090")
        r.quit()
        return True
    except Exception as e:
        print(f"Error patching at {called_from}: {e}")
        return False


def patch_function(ac_path, function_name, patch_fn, label):
    method_location = get_the_evil_method(ac_path, function_name)
    if not method_location:
        print(f"Could not find method {function_name}.")
        return

    print(f"Found method {function_name} @ {method_location}")
    called_from = find_the_call(ac_path, method_location)
    print(f"Looks like it's called from: {called_from}")

    if not called_from or called_from == [""]:
        print("Patching Failed, maybe already done?")
        return

    for cf in called_from:
        if patch_fn(ac_path, cf):
            print(f"Patching {label} Completed Successfully")
        else:
            print(f"Patching {label} Failed, maybe already done?")


def main():
    if os.geteuid() != 0:
        print("Error: this script must be run as root (sudo), to patch the "
              "binary and manage the vpnagentd service.")
        sys.exit(1)

    ac_path = find_ac_path()
    if ac_path is None:
        print("Could not find vpnagentd under any known install path: "
              f"{', '.join(CANDIDATE_AC_PATHS)}")
        sys.exit(1)
    print(f"Using AnyConnect/Secure Client install at {ac_path}")

    ## Stop the Anyconnect service.
    os.system("systemctl stop vpnagentd")

    ## Patch 1: stop vpnagentd from locking/overwriting the route table.
    patch_function(ac_path, "StartInterface", nop_the_call, "StartInterface")

    ## Patch 2: skip the agent's own binary-signature verification.
    print("Now patching FileSignature verification")
    patch_function(
        ac_path,
        "VerifyFileSignatureCollective::IsValid",
        patch_call_return_zero,
        "FileSignature verification",
    )

    ## Restart the Anyconnect service.
    os.system("systemctl restart vpnagentd")


if __name__ == "__main__":
    main()
