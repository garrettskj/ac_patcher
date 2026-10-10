Notes on the open GitHub issues as of 2026-10-10. These are assessments, not
fixes: none were reproduced against a real binary in this pass, so treat the
root-cause theories below as starting points for whoever picks an issue up,
not confirmed diagnoses.

## #1 - The VPN client failed to establish a connection (4.9.01095)

Intermittent connect failures after accepting the banner, plus `vpnagentd`
repeatedly overwriting `/etc/resolv.conf` even with `chattr +i` set. This
looks like normal AnyConnect DNS-takeover/route behavior rather than
something this patcher's two NOPs would cause or fix. May be server-side or
a separate DNS-protection feature in that build fighting the `chattr` lock.
Needs a packet/debug session against the reporter's specific VPN headend to
say more.

## #2 - MacOS support?

Feature request, not a bug. Current script assumes Linux: it hardcodes
`systemctl stop/restart vpnagentd` (macOS uses launchd/launchctl instead),
and the binary path/offsets differ. Also interacts with the Mach-O write
issue described under #13. Real porting effort: service management layer
plus binary-format handling, not a one-line patch.

## #3 - Patching old 3.1 version of anyconnect

Patch runs and reports success under both radare2 2.3 and 4.6, but
`vpnagentd` then fails at
`../../vpn/Agent/MainThread.cpp Line: 341, CHostConfigMgr::StartInterfaceMonitoring, Return Code: 130974320`.
Possible the found call site is correct for the older binary layout but the
NOP breaks an invariant elsewhere (different calling convention/stack usage
in this much older build), or the located symbol isn't the right call.
Would need the actual 3.1 binary and an r2 session to disassemble around
the patched address and compare against what 4.8+ builds look like there.

## #4 - Failed to patch 4.8.03052 in OSX

Patch reports success, but the VPN service won't start afterward, with a
`com.apple.xpc.launchd` log line: "Binary is improperly signed." This is
expected macOS behavior, not really a patcher bug: patching invalidates the
binary's code signature, and macOS (Gatekeeper/SIP) refuses to run an
improperly signed binary out of `/opt/cisco`. Workaround to document:
re-sign after patching with `codesign --sign - --force
/opt/cisco/anyconnect/bin/vpnagentd` (ad-hoc signature); depending on
entitlements this may also require relaxing SIP for that binary. Untested
here, no macOS box in this pass.

## #5 - Not working on 4.10.03104

Patches cleanly but the VPN doesn't start afterward. No logs attached to the
issue, so no root-cause theory beyond "something in this build's startup
path depends on code at or near the patched call sites." Needs the reporter
(or someone on this version) to attach `journalctl -u vpnagentd` output.

## #8 - Not working with 4.10.05085

Patch completes successfully, but the AnyConnect UI freezes afterward. No
logs attached. Unclear whether this is the patcher breaking something or an
unrelated UI/service freeze on that build. Needs a repro with logs.

## #13 - Some error on 5.0.05040 (macOS version)

Patched `vpnagentd` balloons from ~2.7MB to ~4GB, and the second patch
(`VerifyFileSignatureCollective::IsValid`) fails outright ("called from:
['']"). Likely cause: `r2pipe.open(..., flags=['-w'])` leaves virtual
addressing (`io.va`) on by default. macOS Mach-O binaries load at a high
virtual base (`0x100000000`+), so writing (`wx`) at a virtual address with
`io.va` enabled makes radare2 sparse-grow the underlying file to cover that
address range instead of writing at the real file offset - producing the
multi-GB file seen in the log. A fix would open the file with physical
addressing instead (e.g. `e io.va=false` before the `wx`, or open with the
`-n` flag to skip Mach-O load-command mapping), so writes land at the true
file offset regardless of binary format. Not attempted in code here since
there's no macOS Mach-O AnyConnect binary in this environment to verify the
fix against - would want to confirm it doesn't just move the bug for the
*first* patch (`StartInterface`), which appears to have "succeeded" in the
log despite the file-size blowup, meaning that one may already be writing
to the wrong location even though it didn't error.
