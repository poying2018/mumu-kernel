"""Locate the manager identity constants in an uncompressed kernel.

The manager certificate hash is a plain 64 character string. The certificate
length is an integer constant that the comparison uses, so the code that
references the string is searched for that immediate value.

Usage: locate_identity.py <vmlinux> <hash> <size>
"""
import re
import struct
import sys


def main(vmlinux_path, want_hash, want_size):
    data = open(vmlinux_path, "rb").read()
    want = want_hash.encode()
    size = int(want_size, 0)

    offsets = [m.start() for m in re.finditer(re.escape(want), data)]
    print("hash string occurrences: %d" % len(offsets))
    if not offsets:
        print("the manager hash was not found")
        return 1

    size_needle = struct.pack("<I", size)
    size_hits = [m.start() for m in re.finditer(re.escape(size_needle), data)]

    for off in offsets:
        print("hash at 0x%x" % off)
        near = [h for h in size_hits if abs(h - off) < 0x4000]
        print("  0x%x occurrences within 16 KiB: %s" % (size, [hex(h) for h in near]))
        for h in near:
            print("    context: %s" % data[h - 16:h + 16].hex())

    with open("identity.txt", "w") as f:
        f.write("hash 0x%x size %d\n" % (offsets[0], size))
    print("wrote identity.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
