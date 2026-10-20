#!/usr/bin/env python3
"""Check a kernel module's symbol CRCs against a kernel's Module.symvers.

The emulator ships /system/lib64/vaddress.ko, which is loaded during boot and
provides the binder channel the Android framework needs. Its symbol CRCs have
to match the running kernel or the loader rejects it.

Usage: check-ko-crc.py <Module.symvers> <module.ko>
"""
import subprocess
import sys


def load_symvers(path):
    table = {}
    for line in open(path):
        parts = line.split()
        if len(parts) >= 3:
            table[parts[0]] = parts[1]
    return table


def main(symvers_path, ko_path):
    table = load_symvers(symvers_path)
    out = subprocess.run(
        ["modprobe", "--dump-modversions", ko_path],
        capture_output=True, text=True)
    if out.returncode != 0:
        print("modprobe failed:", out.stderr[:300])
        return 2

    total = 0
    bad = 0
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        name, crc = parts[0], parts[1]
        if not name or not crc:
            continue
        total += 1
        if name not in table:
            print("  no such symbol: %s" % name)
            bad += 1
        elif table[name] != crc:
            print("  crc mismatch: %s module=%s kernel=%s" % (name, crc, table[name]))
            bad += 1

    print("checked %d symbols, %d mismatches" % (total, bad))
    if bad:
        return 1
    print("all symbol CRCs match")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
