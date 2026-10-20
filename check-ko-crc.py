#!/usr/bin/env python3
"""Check a kernel module's symbol CRCs against a kernel's CRC list.

The emulator ships /system/lib64/vaddress.ko, loaded during boot to provide
the binder channel the Android framework needs. Its symbol CRCs must match
the running kernel or the loader rejects it.

The kernel side is a two column list of "symbol crc" lines; the module side
is read straight from its __versions section, so no modprobe is needed.

Usage: check-ko-crc.py <crc list> <module.ko>
"""
import struct
import sys

VERSIONS_SIZE = 64


def load_kernel_crcs(path):
    table = {}
    for line in open(path):
        parts = line.split()
        if len(parts) >= 2:
            table[parts[0]] = parts[1].lstrip("0").rjust(8, "0")
    return table


def load_module_crcs(path):
    data = open(path, "rb").read()
    sh_off = struct.unpack_from("<Q", data, 0x28)[0]
    sh_ent = struct.unpack_from("<H", data, 0x3A)[0]
    sh_num = struct.unpack_from("<H", data, 0x3C)[0]
    sh_str = struct.unpack_from("<H", data, 0x3E)[0]
    secs = [struct.unpack_from("<IIQQQQIIQQ", data, sh_off + i * sh_ent)
            for i in range(sh_num)]
    strtab = secs[sh_str][4]
    for s in secs:
        off = strtab + s[0]
        end = data.index(b"\x00", off)
        if data[off:end].decode() != "__versions":
            continue
        base, size = s[4], s[5]
        out = {}
        for i in range(size // VERSIONS_SIZE):
            entry = base + i * VERSIONS_SIZE
            crc = struct.unpack_from("<I", data, entry)[0]
            no = entry + 8
            ne = data.index(b"\x00", no)
            out[data[no:ne].decode()] = "%08x" % crc
        return out
    return {}


def main(crc_path, ko_path):
    kernel = load_kernel_crcs(crc_path)
    module = load_module_crcs(ko_path)
    print("kernel symbols: %d, module symbols: %d" % (len(kernel), len(module)))
    bad = 0
    for name, crc in sorted(module.items()):
        if name not in kernel:
            print("  no such symbol: %s" % name)
            bad += 1
        elif kernel[name] != crc:
            print("  crc mismatch: %s module=%s kernel=%s" % (name, crc, kernel[name]))
            bad += 1
    print("checked %d symbols, %d mismatches" % (len(module), bad))
    if bad:
        return 1
    print("all symbol CRCs match")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
