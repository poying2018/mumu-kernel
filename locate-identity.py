#!/usr/bin/env python3
"""Locate the manager identity constants in a kernel image.

The manager certificate hash is a plain 64 character string in the image.
The certificate length the comparison uses is an integer constant; it sits in
the code that references the string, so the region around the string is
searched for it.

Usage: locate-identity.py <kernel image> <expected hash>
"""
import re
import struct
import sys


def main(image_path, want_hash):
    data = open(image_path, "rb").read()
    want = want_hash.encode()

    offsets = [m.start() for m in re.finditer(re.escape(want), data)]
    if not offsets:
        print("the hash string was not found")
        return 1

    for off in offsets:
        print("hash string at 0x%x" % off)
        # The size constant is compared against the length of the
        # certificate, so look for it close to the string.
        needle = struct.pack("<I", 0x33B)
        hits = [m.start() for m in re.finditer(re.escape(needle), data)]
        near = [h for h in hits if abs(h - off) < 0x8000]
        print("  0x33b occurrences within 32 KiB: %s" % [hex(h) for h in near])
        print("  0x33b occurrences in the whole image: %d" % len(hits))
        for h in near:
            print("    at 0x%x context: %s" % (h, data[h - 16:h + 16].hex()))

    with open("hash_offset.txt", "w") as f:
        f.write("0x%x" % offsets[0])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
