#!/usr/bin/env python3
"""Extract the uncompressed vmlinux from a bzImage.

Usage: extract-vmlinux.py <bzImage> <output>
"""
import gzip
import lzma
import struct
import subprocess
import sys

MAGICS = [
    (b"\x1f\x8b\x08", "gzip"),
    (b"\xfd7zXZ", "xz"),
    (b"\x28\xb5\x2f\xfd", "zstd"),
    (b"\x89LZO", "lzo"),
]


def main(img_path, out_path):
    data = open(img_path, "rb").read()
    po = struct.unpack_from("<I", data, 0x248)[0]
    pl = struct.unpack_from("<I", data, 0x24C)[0]
    payload = data[po:po + pl]

    found = None
    for magic, kind in MAGICS:
        idx = payload.find(magic)
        if 0 <= idx < len(payload):
            found = (kind, magic, idx)
            break

    if not found:
        print("no compression magic found in the payload")
        return 2

    kind, magic, idx = found
    blob = payload[idx:]
    print("found %s at payload+0x%x" % (kind, idx))

    if kind == "gzip":
        out = gzip.decompress(blob)
    elif kind == "xz":
        out = lzma.decompress(blob)
    elif kind == "zstd":
        proc = subprocess.run(["zstd", "-d", "-c"], input=blob, capture_output=True)
        out = proc.stdout
    else:
        print("unsupported compression: %s" % kind)
        return 2

    open(out_path, "wb").write(out)
    print("wrote %s (%d bytes)" % (out_path, len(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
